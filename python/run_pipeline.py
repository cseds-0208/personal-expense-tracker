"""
Data Pipeline Orchestrator
--------------------------
Executes the end-to-end data pipeline:
1. Generates synthetic raw transaction dataset (600+ records)
2. Runs comprehensive cleaning and hygiene audits
3. Produces standardized datasets for Oracle SQL and Power BI
4. Generates data quality report and Oracle SQL insert scripts
"""

import os
import json
import pandas as pd
from datetime import datetime

from python.generate_dataset import generate_raw_dataset
from python.data_cleaning import clean_and_preprocess_transactions
from python.analysis import (
    DEFAULT_CATEGORY_BUDGETS,
    calculate_monthly_financial_summary,
    analyze_category_budgets,
    compute_month_over_month_trends,
    generate_financial_insights
)


def run_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    proc_dir = os.path.join(base_dir, "data", "processed")
    reports_dir = os.path.join(base_dir, "reports")
    sql_dir = os.path.join(base_dir, "oracle_sql")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(sql_dir, exist_ok=True)

    raw_csv_path = os.path.join(raw_dir, "sample_expenses_raw.csv")
    benchmark_csv_path = os.path.join(base_dir, "data", "sample_expenses.csv")
    clean_csv_path = os.path.join(proc_dir, "clean_transactions.csv")

    # Step 1: Generate Raw Dataset (620 rows)
    raw_df = generate_raw_dataset(raw_csv_path, count=620)

    # Step 2: Clean and Preprocess
    cleaned_df, audit = clean_and_preprocess_transactions(raw_df)

    # Step 3: Export Primary Sample Expenses and Processed Transactions
    cleaned_df.to_csv(benchmark_csv_path, index=False)
    cleaned_df.to_csv(clean_csv_path, index=False)
    print(f"Exported clean benchmark dataset: {len(cleaned_df)} records -> {benchmark_csv_path}")

    # Step 4: Generate Dimension Tables for Star Schema & Oracle SQL
    # Categories Dimension
    categories_data = [
        {"category_id": 1, "category_name": "Salary", "category_type": "INCOME", "description": "Primary and secondary employment earnings", "is_active": "Y"},
        {"category_id": 2, "category_name": "Housing", "category_type": "FIXED", "description": "Residential rent, maintenance, and home upkeep", "is_active": "Y"},
        {"category_id": 3, "category_name": "Food & Dining", "category_type": "DISCRETIONARY", "description": "Groceries, food delivery, dining out, and cafes", "is_active": "Y"},
        {"category_id": 4, "category_name": "Transportation", "category_type": "DISCRETIONARY", "description": "Vehicle fuel, cabs, public transit, and tolls", "is_active": "Y"},
        {"category_id": 5, "category_name": "Shopping", "category_type": "DISCRETIONARY", "description": "Apparel, electronics, retail, and household items", "is_active": "Y"},
        {"category_id": 6, "category_name": "Utilities", "category_type": "FIXED", "description": "Electricity, water, broadband, gas, and mobile bills", "is_active": "Y"},
        {"category_id": 7, "category_name": "Healthcare", "category_type": "DISCRETIONARY", "description": "Doctor fees, pharmacy, diagnostic tests, and clinics", "is_active": "Y"},
        {"category_id": 8, "category_name": "Entertainment", "category_type": "DISCRETIONARY", "description": "OTT streaming, cinema tickets, gaming, and events", "is_active": "Y"},
        {"category_id": 9, "category_name": "Education", "category_type": "DISCRETIONARY", "description": "Courses, certifications, books, and training programs", "is_active": "Y"},
        {"category_id": 10, "category_name": "Travel", "category_type": "DISCRETIONARY", "description": "Flights, hotels, outstation trips, and vacations", "is_active": "Y"},
        {"category_id": 11, "category_name": "Other", "category_type": "OTHER", "description": "Miscellaneous and contingency outlays", "is_active": "Y"},
        {"category_id": 12, "category_name": "Uncategorised", "category_type": "OTHER", "description": "Unclassified gateway or merchant debits requiring review", "is_active": "Y"},
    ]
    categories_df = pd.DataFrame(categories_data)
    cat_map = {row["category_name"]: row["category_id"] for row in categories_data}
    categories_df.to_csv(os.path.join(proc_dir, "categories.csv"), index=False)

    # Payment Methods Dimension
    pm_data = [
        {"payment_method_id": 1, "method_name": "Net Banking", "channel_type": "BANKING", "is_active": "Y"},
        {"payment_method_id": 2, "method_name": "UPI", "channel_type": "DIGITAL", "is_active": "Y"},
        {"payment_method_id": 3, "method_name": "Credit Card", "channel_type": "CREDIT", "is_active": "Y"},
        {"payment_method_id": 4, "method_name": "Debit Card", "channel_type": "BANKING", "is_active": "Y"},
        {"payment_method_id": 5, "method_name": "Cash", "channel_type": "PHYSICAL", "is_active": "Y"},
        {"payment_method_id": 6, "method_name": "Other", "channel_type": "DIGITAL", "is_active": "Y"},
    ]
    pd.DataFrame(pm_data).to_csv(os.path.join(proc_dir, "dim_payment_methods.csv"), index=False)

    # Monthly Budget Fact / Dimension
    budget_rows = []
    budget_id = 1
    # For Oct 2026, Nov 2026, Dec 2026
    for y in [2026]:
        for m in [10, 11, 12]:
            for cat_name, amt in DEFAULT_CATEGORY_BUDGETS.items():
                budget_rows.append({
                    "budget_id": budget_id,
                    "category_id": cat_map[cat_name],
                    "category_name": cat_name,
                    "budget_month": m,
                    "budget_year": y,
                    "budget_amount": amt
                })
                budget_id += 1
    budget_df = pd.DataFrame(budget_rows)
    budget_df.to_csv(os.path.join(proc_dir, "monthly_budget.csv"), index=False)

    # Date Dimension (for Power BI Star Schema)
    date_records = []
    for d in pd.date_range("2026-10-01", "2026-12-31"):
        date_records.append({
            "date": d.strftime("%Y-%m-%d"),
            "year": d.year,
            "quarter": f"Q{d.quarter}",
            "month": d.month,
            "month_name": d.strftime("%B"),
            "month_year": d.strftime("%b %Y"),
            "day": d.day,
            "day_name": d.strftime("%A"),
            "is_weekend": "Y" if d.weekday() >= 5 else "N",
            "is_month_end": "Y" if d.is_month_end else "N"
        })
    pd.DataFrame(date_records).to_csv(os.path.join(proc_dir, "dim_date.csv"), index=False)

    # Step 5: Generate Formal Data Quality Report (Markdown)
    dq_report_content = f"""# Data Quality & Hygiene Audit Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** Personal Expense Tracker and Budget Dashboard  
**Source File:** `data/raw/sample_expenses_raw.csv`  
**Output Target:** `data/processed/clean_transactions.csv`  

---

## 1. Executive Summary Metrics

| Metric | Count | Percentage |
|---|---|---|
| **Total Input Raw Records** | **{audit.total_input_records}** | 100.0% |
| **Valid Clean Records Retained** | **{audit.valid_records}** | {(audit.valid_records/audit.total_input_records*100):.2f}% |
| **Quarantined Invalid Records** | **{audit.invalid_records}** | {(audit.invalid_records/audit.total_input_records*100):.2f}% |
| **Duplicate Records Detected** | **{audit.duplicate_count}** | {(audit.duplicate_count/audit.total_input_records*100):.2f}% |
| **Missing / Null Value Rows** | **{audit.missing_value_count}** | {(audit.missing_value_count/audit.total_input_records*100):.2f}% |
| **Uncategorised Transactions** | **{audit.uncategorised_count}** | {(audit.uncategorised_count/audit.valid_records*100):.2f}% |
| **Merchant Refund Reversals** | **{audit.refund_count}** | {(audit.refund_count/audit.valid_records*100):.2f}% |

---

## 2. Ingestion & Hygiene Policy Applied

1. **Zero Silent Discard Policy**: Every single rejected row was inspected and cataloged with specific reason codes.
2. **Missing Dates & Descriptions**: Rows with null or empty timestamps or descriptions were quarantined into the audit log rather than imputed with guess work.
3. **Amount Validation**: Negative amounts or non-numeric corrupted strings were flagged and quarantined.
4. **Duplicate Handling**: Exact duplicate rows and duplicate business entries (matching `date`, `description`, `amount`, and `payment_method`) were flagged and isolated.
5. **Refund Identification**: Reversals containing refund indicators were classified as `REFUND` type and properly offset expenses rather than inflating spending or income.
6. **Uncategorised Preservation**: Ambiguous vendor tokens were preserved under the category `Uncategorised` rather than being assigned arbitrary labels.

---

## 3. Data Cleaning Pipeline Actions
"""
    for act in audit.cleaning_actions:
        dq_report_content += f"- {act}\n"

    dq_report_content += "\n## 4. Quarantined Records Audit Sample\n\n"
    dq_report_content += "| Row # | Reason | Details |\n|---|---|---|\n"
    for ex in audit.excluded_records:
        r_idx = ex.get("row_index", "N/A")
        reason = ex.get("reason", "Unknown")
        raw = str(ex.get("raw_record", {}))[:70] + "..."
        dq_report_content += f"| {r_idx} | {reason} | `{raw}` |\n"

    with open(os.path.join(reports_dir, "data_quality_report.md"), "w", encoding="utf-8") as f:
        f.write(dq_report_content)
    print("Generated reports/data_quality_report.md")

    # Step 6: Generate Oracle SQL Data Insertion Script (02_insert_data.sql)
    generate_oracle_insert_sql(cleaned_df, categories_data, pm_data, budget_rows, sql_dir)

    # Step 7: Generate Insights Summary Report
    insights_data = generate_financial_insights(cleaned_df)
    generate_insights_report(insights_data, os.path.join(reports_dir, "insights_summary.md"))


def generate_oracle_insert_sql(cleaned_df, categories_data, pm_data, budget_rows, sql_dir):
    """Generates 02_insert_data.sql with Oracle-compatible INSERT statements."""
    sql_path = os.path.join(sql_dir, "02_insert_data.sql")
    cat_map = {row["category_name"]: row["category_id"] for row in categories_data}

    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- =============================================================================\n")
        f.write("-- SCRIPT 02: ORACLE DATA INSERTION (DML)\n")
        f.write("-- PROJECT: Personal Expense Tracker and Budget Dashboard\n")
        f.write("-- =============================================================================\n\n")
        f.write("SET DEFINE OFF;\nSET AUTOCOMMIT OFF;\n\n")

        # Categories
        f.write("-- 1. INSERT CATEGORIES\n")
        for cat in categories_data:
            f.write(
                f"INSERT INTO CATEGORIES (CATEGORY_ID, CATEGORY_NAME, CATEGORY_TYPE, DESCRIPTION, IS_ACTIVE) "
                f"VALUES ({cat['category_id']}, '{cat['category_name']}', '{cat['category_type']}', '{cat['description']}', '{cat['is_active']}');\n"
            )
        f.write("COMMIT;\n\n")

        # Payment Methods
        f.write("-- 2. INSERT PAYMENT METHODS\n")
        for pm in pm_data:
            f.write(
                f"INSERT INTO PAYMENT_METHODS (PAYMENT_METHOD_ID, METHOD_NAME, CHANNEL_TYPE, IS_ACTIVE) "
                f"VALUES ({pm['payment_method_id']}, '{pm['method_name']}', '{pm['channel_type']}', '{pm['is_active']}');\n"
            )
        f.write("COMMIT;\n\n")

        # Monthly Budget
        f.write("-- 3. INSERT MONTHLY BUDGETS\n")
        for b in budget_rows:
            f.write(
                f"INSERT INTO MONTHLY_BUDGET (BUDGET_ID, CATEGORY_ID, BUDGET_MONTH, BUDGET_YEAR, BUDGET_AMOUNT) "
                f"VALUES ({b['budget_id']}, {b['category_id']}, {b['budget_month']}, {b['budget_year']}, {b['budget_amount']:.2f});\n"
            )
        f.write("COMMIT;\n\n")

        # Transactions
        f.write("-- 4. INSERT CLEAN TRANSACTIONS (Batch Commits)\n")
        txn_counter = 1
        for _, row in cleaned_df.iterrows():
            c_id = cat_map.get(row["category"], 12)  # default to Uncategorised (12)
            desc_escaped = str(row["description"]).replace("'", "''")
            notes_escaped = str(row["notes"]).replace("'", "''")
            d_str = row["transaction_date"].strftime("%Y-%m-%d")

            f.write(
                f"INSERT INTO TRANSACTIONS (TRANSACTION_ID, TRANSACTION_DATE, DESCRIPTION, AMOUNT, "
                f"CATEGORY_ID, TRANSACTION_TYPE, PAYMENT_METHOD, NOTES, SOURCE_RAW_ID) "
                f"VALUES ({txn_counter}, TO_DATE('{d_str}', 'YYYY-MM-DD'), '{desc_escaped}', {row['amount']:.2f}, "
                f"{c_id}, '{row['transaction_type']}', '{row['payment_method']}', '{notes_escaped}', '{row['transaction_id']}');\n"
            )
            txn_counter += 1
            if txn_counter % 100 == 0:
                f.write("COMMIT;\n")

        f.write("COMMIT;\n\n")
        f.write("PROMPT Sample data population completed successfully.\n")

    print(f"Generated Oracle SQL insert script: {sql_path}")


def generate_insights_report(insights: dict, output_path: str):
    """Generates the formal business intelligence and financial insights report."""
    summary = insights["summary"]
    content = f"""# Executive Financial Insights & Analytics Summary

**Domain:** Banking & Wealth Intelligence  
**Dataset:** Personal Expense Tracker Benchmark Dataset (Q4 2026: Oct - Dec 2026)  
**Report Date:** {datetime.now().strftime('%Y-%m-%d')}  

---

## 1. Executive Performance Dashboard

| Key Performance Indicator | Metric Value | Benchmark / Health Status |
|---|---|---|
| **Total Monthly Income** | ₹{summary['total_income']:,.2f} | Positive Inflow |
| **Gross Living Expenditures** | ₹{summary['gross_expenses']:,.2f} | Outflow |
| **Merchant Refunds Offset** | ₹{summary['total_refunds']:,.2f} | Reversals Applied |
| **Net Operational Expenses** | ₹{summary['net_expenses']:,.2f} | True Financial Drain |
| **Net Savings Surplus** | ₹{summary['savings']:,.2f} | Retained Capital |
| **Personal Savings Rate** | **{summary['savings_rate']:.1f}%** | 🟢 Healthy (> 40% recommended) |
| **Overall Budget Utilization** | **{insights['overall_budget_utilization']:.1f}%** | Tracked vs ₹{insights['total_budget']:,.2f} Budget |
| **Daily Average Burn Rate** | **₹{summary['daily_burn_rate']:,.2f} / day** | Operating Velocity |

---

## 2. Category Variance & Budget Adherence

- **Dominant Expenditure Center:** **{insights['highest_spending_category']}** at **₹{insights['highest_spending_amount']:,.2f}**.
- **Lowest Expenditure Center:** **{insights['lowest_spending_category']}** at **₹{insights['lowest_spending_amount']:,.2f}**.
- **Primary Payment Rail:** **{insights['top_payment_method']}** accounted for the largest aggregate volume.

### Budget Breach Analysis
"""
    if insights["breaches"]:
        content += "| Breached Category | Budget Ceiling | Actual Spend | Overrun % |\n|---|---|---|---|\n"
        for b in insights["breaches"]:
            content += f"| **{b['category']}** | ₹{b['budget_amount']:,.2f} | ₹{b['net_spend']:,.2f} | {b['utilization_pct']:.1f}% |\n"
    else:
        content += "✅ All spending categories remained strictly within established budget ceilings.\n"

    content += "\n## 3. Month-over-Month (MoM) Expenditure Trajectory\n\n"
    content += "| Month | Gross Outflow | Merchant Refunds | Net Expenses | MoM Change (₹) | MoM Growth % |\n|---|---|---|---|---|---|\n"
    for m in insights.get("mom_trends", []):
        chg = f"₹{m.get('mom_spend_change', 0):,.2f}" if pd.notna(m.get('mom_spend_change')) else "-"
        pct = f"{m.get('mom_growth_pct', 0):.2f}%" if pd.notna(m.get('mom_growth_pct')) else "-"
        content += f"| {m['month_year']} | ₹{m['gross_expense']:,.2f} | ₹{m['refunds']:,.2f} | ₹{m['net_expense']:,.2f} | {chg} | {pct} |\n"

    content += "\n## 4. Strategic Financial Observations & Guidance\n\n"
    for note in insights["insights_text"]:
        content += f"- {note}\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    run_pipeline()
