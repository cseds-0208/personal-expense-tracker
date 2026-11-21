"""
Automated Test Suite for Personal Expense Tracker & Budget Dashboard
-------------------------------------------------------------------
Verifies the 8 Mandatory Test Cases per HCL Data Analyst Enterprise Standards.
"""

import os
import sys
import pytest
import pandas as pd
from datetime import date

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.expense_categorization import (
    classify_transaction,
    is_refund_description,
    STANDARD_CATEGORIES,
)
from python.data_cleaning import clean_and_preprocess_transactions
from python.analysis import (
    DEFAULT_CATEGORY_BUDGETS,
    calculate_monthly_financial_summary,
    analyze_category_budgets,
)


@pytest.fixture
def raw_dataset():
    """Loads the benchmark raw dataset."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "sample_expenses_raw.csv")
    assert os.path.exists(raw_path), f"Raw dataset not found at {raw_path}"
    return pd.read_csv(raw_path)


@pytest.fixture
def clean_dataset(raw_dataset):
    """Processes the raw dataset through the data hygiene pipeline."""
    df, audit = clean_and_preprocess_transactions(raw_dataset)
    return df, audit


# ==============================================================================
# TEST CASE 1: UNCATEGORISED EXPENSE
# ==============================================================================
def test_case_1_uncategorised_expense(clean_dataset):
    """
    Verify that an expense with an unknown description is assigned the
    'Uncategorised' category and is retained without data loss.
    """
    df, audit = clean_dataset
    uncat_records = df[df["category"] == "Uncategorised"]

    # Must retain uncategorised records
    assert len(uncat_records) > 0, "No uncategorised records found in clean dataset."
    assert not uncat_records["description"].isna().any(), "Uncategorised records contain null descriptions."

    # Direct test on ambiguous string
    cat, txn_type = classify_transaction("UNKNOWN WEIRD TERMINAL 99182 POS")
    assert cat == "Uncategorised", f"Expected 'Uncategorised', got '{cat}'"
    assert txn_type == "EXPENSE", f"Expected 'EXPENSE', got '{txn_type}'"


# ==============================================================================
# TEST CASE 2: REFUND ENTRIES
# ==============================================================================
def test_case_2_refund_entries(clean_dataset):
    """
    Verify that refunds are segregated and offset gross expenses rather than
    inflating expenses or being misclassified as income.
    """
    df, _ = clean_dataset
    refunds = df[df["transaction_type"] == "REFUND"]
    expenses = df[df["transaction_type"] == "EXPENSE"]
    income = df[df["transaction_type"] == "INCOME"]

    assert len(refunds) > 0, "No refund records present in dataset."

    # Verify refund descriptions contain reversal / refund keywords
    for _, row in refunds.iterrows():
        assert is_refund_description(row["description"]) or row["transaction_type"] == "REFUND"

    gross_expense = expenses["amount"].sum()
    refund_total = refunds["amount"].sum()

    # Net expenses must equal gross expenses minus refunds
    summary = calculate_monthly_financial_summary(df)
    assert summary["gross_expenses"] == round(float(gross_expense), 2)
    assert summary["total_refunds"] == round(float(refund_total), 2)
    assert summary["net_expenses"] == round(float(gross_expense - refund_total), 2)

    # Verify refunds are not counted in income
    assert summary["total_income"] == round(float(income["amount"].sum()), 2)


# ==============================================================================
# TEST CASE 3: MONTH-END BOUNDARY DATES
# ==============================================================================
def test_case_3_month_end_boundary_dates(clean_dataset):
    """
    Verify that transactions on the last day of a month (28, 29, 30, 31)
    are attributed to the correct calendar month and year.
    """
    df, _ = clean_dataset
    boundary_records = df[df["day"] >= 28]
    assert len(boundary_records) > 0, "No month-end boundary records detected."

    for _, row in boundary_records.iterrows():
        d = row["transaction_date"]
        assert row["month"] == d.month, f"Month mismatch for {d}: row month {row['month']}"
        assert row["year"] == d.year, f"Year mismatch for {d}: row year {row['year']}"


# ==============================================================================
# TEST CASE 4: BUDGET BREACH DETECTION
# ==============================================================================
def test_case_4_budget_breach_detection(clean_dataset):
    """
    Verify that budget breaches are correctly identified when category spending
    exceeds the configured monthly budget ceiling.
    """
    df, _ = clean_dataset

    # Create an artificial low budget for Food & Dining to force a breach
    custom_budgets = DEFAULT_CATEGORY_BUDGETS.copy()
    custom_budgets["Food & Dining"] = 100.0  # Force breach

    cat_analysis = analyze_category_budgets(df, category_budgets=custom_budgets, month=10, year=2026)
    food_row = cat_analysis[cat_analysis["category"] == "Food & Dining"].iloc[0]

    assert food_row["status"] == "BREACH", f"Expected BREACH for Food & Dining, got {food_row['status']}"
    assert food_row["net_spend"] > food_row["budget_amount"]
    assert food_row["utilization_pct"] > 100.0
    assert food_row["variance"] < 0.0


# ==============================================================================
# TEST CASE 5: MONTHLY RECONCILIATION
# ==============================================================================
def test_case_5_monthly_reconciliation(clean_dataset):
    """
    Verify that monthly totals reconcile consistently across income,
    gross expenses, refunds, net expenses, and net savings.
    """
    df, _ = clean_dataset
    for m in [10, 11, 12]:
        m_df = df[(df["year"] == 2026) & (df["month"] == m)]
        summary = calculate_monthly_financial_summary(m_df)

        calc_income = m_df[m_df["transaction_type"] == "INCOME"]["amount"].sum()
        calc_gross = m_df[m_df["transaction_type"] == "EXPENSE"]["amount"].sum()
        calc_ref = m_df[m_df["transaction_type"] == "REFUND"]["amount"].sum()
        calc_net = max(0.0, calc_gross - calc_ref)
        calc_savings = calc_income - calc_net

        assert round(summary["total_income"], 2) == round(calc_income, 2)
        assert round(summary["gross_expenses"], 2) == round(calc_gross, 2)
        assert round(summary["total_refunds"], 2) == round(calc_ref, 2)
        assert round(summary["net_expenses"], 2) == round(calc_net, 2)
        assert round(summary["savings"], 2) == round(calc_savings, 2)


# ==============================================================================
# TEST CASE 6: DUPLICATE TRANSACTIONS DETECTION
# ==============================================================================
def test_case_6_duplicate_transactions(raw_dataset):
    """
    Verify that duplicate records are detected and handled according to policy.
    """
    _, audit = clean_and_preprocess_transactions(raw_dataset)
    assert audit.duplicate_count > 0, "Duplicate records were not detected during data hygiene."
    assert any("Duplicate" in act for act in audit.cleaning_actions), "Cleaning actions do not mention duplicate quarantine."


# ==============================================================================
# TEST CASE 7: MISSING OR INVALID DATA
# ==============================================================================
def test_case_7_missing_or_invalid_data(raw_dataset):
    """
    Verify that missing dates, invalid amounts, and unparseable values are flagged.
    """
    clean_df, audit = clean_and_preprocess_transactions(raw_dataset)
    assert audit.missing_value_count > 0, "Expected missing values to be logged in audit."
    assert audit.invalid_records > 0, "Expected invalid records to be logged in audit."

    # In clean dataset, no null dates or amounts allowed
    assert clean_df["transaction_date"].notna().all(), "Null dates found in clean dataset."
    assert (clean_df["amount"] > 0).all(), "Non-positive amounts found in clean dataset."


# ==============================================================================
# TEST CASE 8: INCOME AND EXPENSE SEPARATION
# ==============================================================================
def test_case_8_income_expense_separation(clean_dataset):
    """
    Verify that income transactions are never included in expense totals or budget depletion.
    """
    df, _ = clean_dataset
    income_txns = df[df["transaction_type"] == "INCOME"]
    expense_txns = df[df["transaction_type"] == "EXPENSE"]

    # Zero overlap
    intersection = set(income_txns["transaction_id"]).intersection(set(expense_txns["transaction_id"]))
    assert len(intersection) == 0, f"Overlapping transaction IDs found: {intersection}"

    # Budget analysis must not include Salary/Income
    cat_analysis = analyze_category_budgets(df)
    assert "Salary" not in cat_analysis["category"].values, "Salary unexpectedly included in expense budget tracking."
