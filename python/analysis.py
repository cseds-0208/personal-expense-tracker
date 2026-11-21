"""
Financial Analysis & Business Intelligence Module
-------------------------------------------------
Performs financial calculations, budget variance monitoring,
breach detection, trend analysis, and dynamic insight generation.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


# Standard default category monthly budgets (in INR)
DEFAULT_CATEGORY_BUDGETS: Dict[str, float] = {
    "Housing": 25000.0,
    "Food & Dining": 12000.0,
    "Transportation": 7000.0,
    "Shopping": 8000.0,
    "Utilities": 5000.0,
    "Healthcare": 4000.0,
    "Entertainment": 3500.0,
    "Education": 3000.0,
    "Travel": 6000.0,
    "Other": 2000.0,
    "Uncategorised": 1500.0,
}


def calculate_monthly_financial_summary(
    df: pd.DataFrame,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """Computes high-level financial KPIs for the selected period or entire dataset."""
    filtered_df = df.copy()
    if year:
        filtered_df = filtered_df[filtered_df["year"] == year]
    if month:
        filtered_df = filtered_df[filtered_df["month"] == month]

    income_df = filtered_df[filtered_df["transaction_type"] == "INCOME"]
    expense_df = filtered_df[filtered_df["transaction_type"] == "EXPENSE"]
    refund_df = filtered_df[filtered_df["transaction_type"] == "REFUND"]

    total_income = float(income_df["amount"].sum())
    gross_expenses = float(expense_df["amount"].sum())
    total_refunds = float(refund_df["amount"].sum())

    # Net expenses adjust for merchant refunds
    net_expenses = max(0.0, gross_expenses - total_refunds)
    remaining_balance = total_income - net_expenses
    savings = remaining_balance
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0.0

    # Total days in active period for burn rate
    if not filtered_df.empty:
        min_date = filtered_df["transaction_date"].min()
        max_date = filtered_df["transaction_date"].max()
        days_span = max(1, (max_date - min_date).days + 1)
        daily_burn_rate = net_expenses / days_span
    else:
        daily_burn_rate = 0.0

    return {
        "total_income": round(total_income, 2),
        "gross_expenses": round(gross_expenses, 2),
        "total_refunds": round(total_refunds, 2),
        "net_expenses": round(net_expenses, 2),
        "remaining_balance": round(remaining_balance, 2),
        "savings": round(savings, 2),
        "savings_rate": round(savings_rate, 2),
        "transaction_count": len(filtered_df),
        "daily_burn_rate": round(daily_burn_rate, 2),
    }


def analyze_category_budgets(
    df: pd.DataFrame,
    category_budgets: Optional[Dict[str, float]] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> pd.DataFrame:
    """
    Computes category-wise spend, refunds, net spend, budget variance,
    and breach detection status.
    """
    if category_budgets is None:
        category_budgets = DEFAULT_CATEGORY_BUDGETS

    filtered_df = df.copy()
    if year:
        filtered_df = filtered_df[filtered_df["year"] == year]
    if month:
        filtered_df = filtered_df[filtered_df["month"] == month]

    # Exclude income transactions from expense budget tracking
    non_income_df = filtered_df[filtered_df["transaction_type"].isin(["EXPENSE", "REFUND"])]

    # Aggregate by category and transaction type
    records = []
    all_categories = sorted(list(set(non_income_df["category"].unique()).union(set(category_budgets.keys()))))

    for cat in all_categories:
        if cat == "Salary":
            continue

        cat_data = non_income_df[non_income_df["category"] == cat]
        gross_spend = float(cat_data[cat_data["transaction_type"] == "EXPENSE"]["amount"].sum())
        refunds = float(cat_data[cat_data["transaction_type"] == "REFUND"]["amount"].sum())
        net_spend = max(0.0, gross_spend - refunds)

        budget_amount = float(category_budgets.get(cat, 0.0))
        variance = budget_amount - net_spend

        if budget_amount > 0:
            utilization_pct = (net_spend / budget_amount) * 100.0
            if net_spend > budget_amount:
                status = "BREACH"
            elif utilization_pct >= 85.0:
                status = "WARNING"
            else:
                status = "ON_TRACK"
        else:
            utilization_pct = 0.0
            status = "NO_BUDGET" if net_spend == 0 else "UNBUDGETED_SPEND"

        records.append({
            "category": cat,
            "budget_amount": round(budget_amount, 2),
            "gross_spend": round(gross_spend, 2),
            "refunds": round(refunds, 2),
            "net_spend": round(net_spend, 2),
            "variance": round(variance, 2),
            "utilization_pct": round(utilization_pct, 2),
            "status": status,
            "transaction_count": len(cat_data)
        })

    result_df = pd.DataFrame(records)
    if not result_df.empty:
        total_net = result_df["net_spend"].sum()
        result_df["spending_share_pct"] = (
            (result_df["net_spend"] / total_net * 100.0).round(2) if total_net > 0 else 0.0
        )
        result_df = result_df.sort_values(by="net_spend", ascending=False).reset_index(drop=True)

    return result_df


def compute_month_over_month_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates MoM spending changes and percentage variations."""
    expense_df = df[df["transaction_type"].isin(["EXPENSE", "REFUND"])].copy()
    if expense_df.empty:
        return pd.DataFrame()

    monthly_grp = expense_df.groupby(["year", "month", "month_year"]).apply(
        lambda g: pd.Series({
            "gross_expense": g[g["transaction_type"] == "EXPENSE"]["amount"].sum(),
            "refunds": g[g["transaction_type"] == "REFUND"]["amount"].sum(),
            "transaction_count": len(g)
        }),
        include_groups=False
    ).reset_index()

    monthly_grp["net_expense"] = (monthly_grp["gross_expense"] - monthly_grp["refunds"]).clip(lower=0)
    monthly_grp = monthly_grp.sort_values(by=["year", "month"]).reset_index(drop=True)

    monthly_grp["mom_spend_change"] = monthly_grp["net_expense"].diff()
    monthly_grp["mom_growth_pct"] = (
        (monthly_grp["mom_spend_change"] / monthly_grp["net_expense"].shift(1)) * 100.0
    ).round(2)

    return monthly_grp


def generate_financial_insights(
    df: pd.DataFrame,
    category_budgets: Optional[Dict[str, float]] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """Generates dynamic, data-driven financial intelligence insights."""
    summary = calculate_monthly_financial_summary(df, month=month, year=year)
    cat_analysis = analyze_category_budgets(df, category_budgets=category_budgets, month=month, year=year)
    mom_trends = compute_month_over_month_trends(df)

    # Filter out categories with zero spending for highest/lowest
    active_cats = cat_analysis[cat_analysis["net_spend"] > 0]

    highest_cat = active_cats.iloc[0]["category"] if not active_cats.empty else "N/A"
    highest_spend = active_cats.iloc[0]["net_spend"] if not active_cats.empty else 0.0

    lowest_cat = active_cats.iloc[-1]["category"] if not active_cats.empty else "N/A"
    lowest_spend = active_cats.iloc[-1]["net_spend"] if not active_cats.empty else 0.0

    breached_cats = cat_analysis[cat_analysis["status"] == "BREACH"]
    breached_list = breached_cats[["category", "budget_amount", "net_spend", "utilization_pct"]].to_dict(orient="records")

    total_budget = cat_analysis["budget_amount"].sum()
    total_net_spend = summary["net_expenses"]
    overall_budget_utilization = (total_net_spend / total_budget * 100.0) if total_budget > 0 else 0.0

    # Top payment method
    expense_txns = df[df["transaction_type"] == "EXPENSE"]
    top_pm = "N/A"
    if not expense_txns.empty:
        top_pm = expense_txns.groupby("payment_method")["amount"].sum().idxmax()

    # Strategic commentary generated from actual metrics
    insights_list = [
        f"Highest Expenditure Category: **{highest_cat}** with net spend of ₹{highest_spend:,.2f} "
        f"({active_cats.iloc[0]['spending_share_pct'] if not active_cats.empty else 0}% of total expenses).",
        f"Lowest Expenditure Category: **{lowest_cat}** with net spend of ₹{lowest_spend:,.2f}.",
        f"Overall Budget Utilization: **{overall_budget_utilization:.1f}%** (₹{total_net_spend:,.2f} spent against ₹{total_budget:,.2f} budget).",
        f"Savings Performance: **{summary['savings_rate']:.1f}%** savings rate (Net savings: ₹{summary['savings']:,.2f} on income of ₹{summary['total_income']:,.2f}).",
        f"Average Daily Burn Rate: **₹{summary['daily_burn_rate']:,.2f}/day**.",
        f"Primary Outflow Rail: **{top_pm}** represents the most heavily utilized payment method."
    ]

    if len(breached_list) > 0:
        names = ", ".join([b["category"] for b in breached_list])
        insights_list.append(f"⚠️ Budget Breaches Detected: {len(breached_list)} categories exceeded allocations ({names}). Immediate correction recommended.")
    else:
        insights_list.append("✅ Budget Adherence: All tracked categories remained within established spending ceilings.")

    return {
        "summary": summary,
        "highest_spending_category": highest_cat,
        "highest_spending_amount": highest_spend,
        "lowest_spending_category": lowest_cat,
        "lowest_spending_amount": lowest_spend,
        "breaches": breached_list,
        "overall_budget_utilization": round(overall_budget_utilization, 2),
        "total_budget": round(total_budget, 2),
        "top_payment_method": top_pm,
        "insights_text": insights_list,
        "mom_trends": mom_trends.to_dict(orient="records") if not mom_trends.empty else []
    }
