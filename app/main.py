"""
Personal Expense Tracker & Budget Dashboard
-------------------------------------------
Fintech-grade enterprise data analytics application developed for
HCL Data Analyst Training. Integrates Python data processing, Oracle SQL
schema standards, and Power BI business intelligence modeling.
"""

import os
import sys
from datetime import datetime, date
import pandas as pd
import streamlit as st

# Add project root to Python module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.expense_categorization import (
    STANDARD_CATEGORIES,
    classify_transaction,
    CATEGORY_KEYWORD_RULES,
)
from python.analysis import (
    DEFAULT_CATEGORY_BUDGETS,
    calculate_monthly_financial_summary,
    analyze_category_budgets,
    compute_month_over_month_trends,
    generate_financial_insights,
)
from app.components.ui_helpers import (
    render_kpi,
    plot_category_donut,
    plot_budget_vs_actual_chart,
    plot_monthly_trend_chart,
    plot_payment_methods_chart,
)

# Page configuration
st.set_page_config(
    page_title="FinTrack | Personal Expense & Budget Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_file = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Initialize Session State
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "clean_transactions.csv")
BENCHMARK_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_expenses.csv")


def load_initial_data() -> pd.DataFrame:
    """Loads transaction data from processed store or fallback sample."""
    path = DATA_FILE if os.path.exists(DATA_FILE) else BENCHMARK_FILE
    if os.path.exists(path):
        df = pd.read_csv(path)
        df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(2026).astype(int)
        df["month"] = pd.to_numeric(df["month"], errors="coerce").fillna(10).astype(int)
        return df
    return pd.DataFrame(columns=[
        "transaction_id", "transaction_date", "description", "amount",
        "category", "transaction_type", "payment_method", "notes", "year", "month", "month_year"
    ])


if "transactions_df" not in st.session_state:
    st.session_state["transactions_df"] = load_initial_data()

if "category_budgets" not in st.session_state:
    st.session_state["category_budgets"] = DEFAULT_CATEGORY_BUDGETS.copy()


# --- SIDEBAR NAVIGATION & FILTERS ---
with st.sidebar:
    st.markdown("### 🏦 FinTrack Analytics")
    st.caption("Personal Expense Tracker & Budget Dashboard | HCL Capstone")

    nav_selection = st.radio(
        "Navigation Menu",
        [
            "📊 Dashboard Overview",
            "💸 Expense Management",
            "🎯 Budget Management",
            "🏷️ Automatic Categorization",
            "📜 Transaction History",
            "💡 Financial Insights",
            "🏛️ Oracle SQL & Schema",
        ]
    )

    st.markdown("---")
    st.markdown("#### 🔍 Global Period Filter")
    df_current = st.session_state["transactions_df"]
    
    available_years = sorted(list(df_current["year"].unique())) if not df_current.empty else [2026]
    selected_year = st.selectbox("Select Year", options=["All"] + available_years, index=0)

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    available_months = sorted(list(df_current["month"].unique())) if not df_current.empty else [10, 11, 12]
    month_opts = ["All"] + [f"{m} - {month_names.get(m, '')}" for m in available_months]
    selected_month_str = st.selectbox("Select Month", options=month_opts, index=0)

    filter_year = int(selected_year) if selected_year != "All" else None
    filter_month = int(selected_month_str.split(" - ")[0]) if selected_month_str != "All" else None

    st.markdown("---")
    st.caption("Environment: HCL Training Sandbox | DB: Oracle 19c Ready")


# Apply Global Filters to Active Working View
active_df = df_current.copy()
if filter_year:
    active_df = active_df[active_df["year"] == filter_year]
if filter_month:
    active_df = active_df[active_df["month"] == filter_month]


# ==============================================================================
# PAGE 1: DASHBOARD OVERVIEW
# ==============================================================================
if nav_selection == "📊 Dashboard Overview":
    st.title("Financial Overview & Performance Dashboard")
    st.markdown("Executive command center monitoring real-time personal cash flows, category budgets, and budget breaches.")

    summary = calculate_monthly_financial_summary(active_df)
    cat_budgets = analyze_category_budgets(
        active_df,
        category_budgets=st.session_state["category_budgets"]
    )
    total_budget = cat_budgets["budget_amount"].sum()
    budget_util_pct = (summary["net_expenses"] / total_budget * 100.0) if total_budget > 0 else 0.0

    # Breach Alerts Banner
    breached_cats = cat_budgets[cat_budgets["status"] == "BREACH"]
    if len(breached_cats) > 0:
        names = ", ".join(breached_cats["category"].tolist())
        st.markdown(
            f"""
            <div class="alert-box alert-danger">
                ⚠️ <b>Budget Breach Alert:</b> <b>{len(breached_cats)}</b> categories have exceeded their monthly spending limits: <b>{names}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )

    # Row 1: KPI Metrics Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi("Monthly Income", f"₹{summary['total_income']:,.2f}", "Credited Inflow", "#10b981", "#059669")
    with c2:
        render_kpi("Net Expenses", f"₹{summary['net_expenses']:,.2f}", f"Gross: ₹{summary['gross_expenses']:,.2f} | Ref: ₹{summary['total_refunds']:,.2f}", "#f43f5e", "#e11d48")
    with c3:
        render_kpi("Remaining Balance", f"₹{summary['remaining_balance']:,.2f}", "Retained Surplus", "#38bdf8", "#0284c7")
    with c4:
        render_kpi("Savings Rate", f"{summary['savings_rate']:.1f}%", f"Total Saved: ₹{summary['savings']:,.2f}", "#a855f7", "#7e22ce")
    with c5:
        util_color = "#ef4444" if budget_util_pct > 100 else ("#f59e0b" if budget_util_pct >= 85 else "#10b981")
        render_kpi("Budget Utilization", f"{budget_util_pct:.1f}%", f"Budget: ₹{total_budget:,.2f}", util_color, "#334155")

    st.markdown("---")

    # Row 2: Charts
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.plotly_chart(plot_category_donut(active_df), use_container_width=True)
    with col_right:
        st.plotly_chart(plot_budget_vs_actual_chart(cat_budgets), use_container_width=True)

    # Row 3: Trend & Payment Methods
    t_left, t_right = st.columns([1.2, 0.8])
    with t_left:
        mom_df = compute_month_over_month_trends(df_current)
        st.plotly_chart(plot_monthly_trend_chart(mom_df), use_container_width=True)
    with t_right:
        st.plotly_chart(plot_payment_methods_chart(active_df), use_container_width=True)


# ==============================================================================
# PAGE 2: EXPENSE MANAGEMENT (CRUD MODULE)
# ==============================================================================
elif nav_selection == "💸 Expense Management":
    st.title("Expense Management & Transaction Operations")
    st.markdown("Record new entries, modify transaction details, and audit existing line items.")

    tab_add, tab_edit, tab_view = st.tabs(["➕ Add Transaction", "✏️ Edit / Delete Transaction", "📋 Search & Filter All"])

    with tab_add:
        st.subheader("Record New Financial Transaction")
        with st.form("form_add_txn", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                in_date = st.date_input("Transaction Date", value=date.today())
                in_type = st.selectbox("Transaction Type", ["EXPENSE", "INCOME", "REFUND"])
            with f2:
                in_amount = st.number_input("Amount (₹)", min_value=1.0, value=500.0, step=50.0)
                in_pm = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash", "Other"])
            with f3:
                in_desc = st.text_input("Transaction Description", placeholder="e.g. Swiggy food delivery")
                in_cat_mode = st.selectbox("Category Selection", ["Auto-Classify from Description"] + STANDARD_CATEGORIES)

            in_notes = st.text_input("Notes / Remarks", placeholder="e.g. Team lunch celebration")
            btn_submit = st.form_submit_button("💾 Save Transaction")

            if btn_submit:
                if not in_desc.strip():
                    st.error("Please provide a valid transaction description.")
                else:
                    if in_cat_mode == "Auto-Classify from Description":
                        assigned_cat, detected_type = classify_transaction(in_desc, txn_type=in_type)
                    else:
                        assigned_cat = in_cat_mode

                    new_id = f"TXN-MAN-{len(st.session_state['transactions_df'])+10001}"
                    new_row = {
                        "transaction_id": new_id,
                        "transaction_date": in_date,
                        "description": in_desc.strip(),
                        "amount": float(in_amount),
                        "category": assigned_cat,
                        "transaction_type": in_type,
                        "payment_method": in_pm,
                        "notes": in_notes.strip(),
                        "year": in_date.year,
                        "month": in_date.month,
                        "month_year": in_date.strftime("%Y-%m"),
                        "day": in_date.day
                    }
                    st.session_state["transactions_df"] = pd.concat([
                        st.session_state["transactions_df"],
                        pd.DataFrame([new_row])
                    ], ignore_index=True)
                    st.session_state["transactions_df"].to_csv(DATA_FILE, index=False)
                    st.success(f"Transaction `{new_id}` saved successfully as category **{assigned_cat}**!")

    with tab_edit:
        st.subheader("Edit or Delete an Existing Transaction")
        if st.session_state["transactions_df"].empty:
            st.info("No transactions available to edit.")
        else:
            txn_list = st.session_state["transactions_df"]["transaction_id"].tolist()
            selected_txn_id = st.selectbox("Select Transaction to Modify", options=txn_list)
            txn_row = st.session_state["transactions_df"][st.session_state["transactions_df"]["transaction_id"] == selected_txn_id].iloc[0]

            with st.form("form_edit_txn"):
                e1, e2, e3 = st.columns(3)
                with e1:
                    e_date = st.date_input("Date", value=txn_row["transaction_date"])
                    e_type = st.selectbox("Type", ["EXPENSE", "INCOME", "REFUND"], index=["EXPENSE", "INCOME", "REFUND"].index(txn_row["transaction_type"]) if txn_row["transaction_type"] in ["EXPENSE", "INCOME", "REFUND"] else 0)
                with e2:
                    e_amount = st.number_input("Amount (₹)", min_value=1.0, value=float(txn_row["amount"]))
                    e_pm = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash", "Other"],
                                        index=["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash", "Other"].index(txn_row["payment_method"]) if txn_row["payment_method"] in ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash", "Other"] else 0)
                with e3:
                    e_desc = st.text_input("Description", value=txn_row["description"])
                    cat_idx = STANDARD_CATEGORIES.index(txn_row["category"]) if txn_row["category"] in STANDARD_CATEGORIES else 0
                    e_cat = st.selectbox("Category", STANDARD_CATEGORIES, index=cat_idx)

                e_notes = st.text_input("Notes", value=str(txn_row.get("notes", "")))

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    btn_update = st.form_submit_button("🔄 Update Transaction")
                with b_col2:
                    btn_delete = st.form_submit_button("🗑️ Delete Transaction")

                if btn_update:
                    idx = st.session_state["transactions_df"][st.session_state["transactions_df"]["transaction_id"] == selected_txn_id].index
                    st.session_state["transactions_df"].loc[idx, "transaction_date"] = e_date
                    st.session_state["transactions_df"].loc[idx, "description"] = e_desc
                    st.session_state["transactions_df"].loc[idx, "amount"] = float(e_amount)
                    st.session_state["transactions_df"].loc[idx, "category"] = e_cat
                    st.session_state["transactions_df"].loc[idx, "transaction_type"] = e_type
                    st.session_state["transactions_df"].loc[idx, "payment_method"] = e_pm
                    st.session_state["transactions_df"].loc[idx, "notes"] = e_notes
                    st.session_state["transactions_df"].to_csv(DATA_FILE, index=False)
                    st.success(f"Transaction `{selected_txn_id}` updated successfully!")
                    st.rerun()

                if btn_delete:
                    st.session_state["transactions_df"] = st.session_state["transactions_df"][
                        st.session_state["transactions_df"]["transaction_id"] != selected_txn_id
                    ].reset_index(drop=True)
                    st.session_state["transactions_df"].to_csv(DATA_FILE, index=False)
                    st.warning(f"Transaction `{selected_txn_id}` deleted.")
                    st.rerun()

    with tab_view:
        st.subheader("Filter and Search Ledger")
        s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
        with s_col1:
            search_query = st.text_input("Search Description or Transaction ID", placeholder="e.g. Swiggy, Netflix, Amazon")
        with s_col2:
            cat_filter = st.multiselect("Filter Categories", options=STANDARD_CATEGORIES, default=[])
        with s_col3:
            type_filter = st.multiselect("Filter Type", options=["EXPENSE", "INCOME", "REFUND"], default=[])

        view_df = active_df.copy()
        if search_query.strip():
            view_df = view_df[
                view_df["description"].str.contains(search_query, case=False, na=False) |
                view_df["transaction_id"].str.contains(search_query, case=False, na=False)
            ]
        if cat_filter:
            view_df = view_df[view_df["category"].isin(cat_filter)]
        if type_filter:
            view_df = view_df[view_df["transaction_type"].isin(type_filter)]

        st.dataframe(
            view_df[["transaction_id", "transaction_date", "description", "category", "transaction_type", "amount", "payment_method", "notes"]],
            use_container_width=True,
            height=400
        )
        st.caption(f"Showing {len(view_df)} transactions matching criteria.")


# ==============================================================================
# PAGE 3: BUDGET MANAGEMENT
# ==============================================================================
elif nav_selection == "🎯 Budget Management":
    st.title("Budget Governance & Allocation Module")
    st.markdown("Set monthly category spending ceilings, evaluate real-time utilization, and detect budget breaches.")

    cat_analysis = analyze_category_budgets(
        active_df,
        category_budgets=st.session_state["category_budgets"],
        month=filter_month,
        year=filter_year
    )

    b1, b2, b3 = st.columns(3)
    total_b = cat_analysis["budget_amount"].sum()
    total_s = cat_analysis["net_spend"].sum()
    total_v = total_b - total_s
    with b1:
        render_kpi("Total Allocated Budget", f"₹{total_b:,.2f}", "Monthly Spending Cap", "#38bdf8")
    with b2:
        render_kpi("Total Net Spend", f"₹{total_s:,.2f}", "Actual Outlay", "#f43f5e" if total_s > total_b else "#10b981")
    with b3:
        v_col = "#10b981" if total_v >= 0 else "#ef4444"
        render_kpi("Budget Variance", f"₹{abs(total_v):,.2f}", "Surplus" if total_v >= 0 else "Overrun Deficit", v_col)

    st.markdown("### Category Budget Status & Breach Indicators")

    # Format status badges
    def format_status(val):
        if val == "BREACH":
            return "🔴 BREACH"
        elif val == "WARNING":
            return "🟡 WARNING (≥85%)"
        elif val == "ON_TRACK":
            return "🟢 ON TRACK"
        return "⚪ NO BUDGET"

    display_df = cat_analysis.copy()
    display_df["status_indicator"] = display_df["status"].apply(format_status)
    display_df["utilization_pct"] = display_df["utilization_pct"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(
        display_df[["category", "budget_amount", "gross_spend", "refunds", "net_spend", "variance", "utilization_pct", "status_indicator"]],
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("⚙️ Update Monthly Category Budgets")
    with st.expander("Click to Modify Category Budgets"):
        with st.form("form_update_budgets"):
            cols = st.columns(3)
            new_budgets = {}
            for i, (cat, cur_amt) in enumerate(st.session_state["category_budgets"].items()):
                with cols[i % 3]:
                    new_val = st.number_input(f"{cat} Budget (₹)", min_value=0.0, value=float(cur_amt), step=500.0)
                    new_budgets[cat] = float(new_val)
            btn_save_budgets = st.form_submit_button("💾 Save Budget Configuration")
            if btn_save_budgets:
                st.session_state["category_budgets"] = new_budgets
                st.success("Category budgets updated successfully!")
                st.rerun()


# ==============================================================================
# PAGE 4: AUTOMATIC CATEGORIZATION
# ==============================================================================
elif nav_selection == "🏷️ Automatic Categorization":
    st.title("Automated Expense Categorization Engine")
    st.markdown("Python rule-based NLP taxonomy engine. Unrecognized merchant entries safely default to `Uncategorised`.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🧪 Test Interactive Categorization")
        test_desc = st.text_input("Enter Transaction Description to Classify", value="Swiggy Instant Delivery BLR")
        if st.button("🔍 Classify Transaction"):
            cat, t_type = classify_transaction(test_desc)
            st.markdown(f"""
            <div class="alert-box alert-info">
                Result for <i>'{test_desc}'</i>:<br>
                Category: <b>{cat}</b><br>
                Inferred Type: <b>{t_type}</b>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📖 Active Keyword Rules Dictionary")
        rule_cat = st.selectbox("View Rules for Category", list(CATEGORY_KEYWORD_RULES.keys()))
        st.write(CATEGORY_KEYWORD_RULES[rule_cat])

    with col2:
        st.subheader("⚠️ Uncategorised Expenses Review")
        uncat_df = df_current[df_current["category"] == "Uncategorised"]
        st.caption(f"Found {len(uncat_df)} transactions requiring categorization review.")

        if not uncat_df.empty:
            st.dataframe(uncat_df[["transaction_id", "transaction_date", "description", "amount", "payment_method"]], use_container_width=True)

            st.markdown("#### Manual Category Override")
            with st.form("form_override_cat"):
                sel_uncat_id = st.selectbox("Select Uncategorised Transaction", uncat_df["transaction_id"].tolist())
                new_assigned_cat = st.selectbox("Assign Correct Category", STANDARD_CATEGORIES)
                if st.form_submit_button("Apply Correction"):
                    idx = st.session_state["transactions_df"][st.session_state["transactions_df"]["transaction_id"] == sel_uncat_id].index
                    st.session_state["transactions_df"].loc[idx, "category"] = new_assigned_cat
                    st.session_state["transactions_df"].to_csv(DATA_FILE, index=False)
                    st.success(f"Transaction `{sel_uncat_id}` reassigned to **{new_assigned_cat}**!")
                    st.rerun()
        else:
            st.success("All transactions are categorized! Zero uncategorised records present.")


# ==============================================================================
# PAGE 5: TRANSACTION HISTORY & AUDIT
# ==============================================================================
elif nav_selection == "📜 Transaction History":
    st.title("Transaction History & Ledger Audit")
    st.markdown("Complete historical transaction repository with date-range filters, refund separation, and CSV export.")

    # Refund Highlights
    refunds_df = active_df[active_df["transaction_type"] == "REFUND"]
    st.caption(f"Active Filter: {len(active_df)} Total Records | {len(refunds_df)} Refunds Identified.")

    st.dataframe(
        active_df[[
            "transaction_id", "transaction_date", "description", "amount",
            "category", "transaction_type", "payment_method", "notes"
        ]],
        use_container_width=True,
        height=500
    )

    # Export functionality
    csv_bytes = active_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Ledger as CSV",
        data=csv_bytes,
        file_name=f"transactions_export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# ==============================================================================
# PAGE 6: FINANCIAL INSIGHTS & DATA QUALITY
# ==============================================================================
elif nav_selection == "💡 Financial Insights":
    st.title("Financial Insights & Business Intelligence")
    st.markdown("Data-driven analytical observations, Pareto analysis, and data hygiene reports.")

    insights = generate_financial_insights(active_df, category_budgets=st.session_state["category_budgets"])

    st.subheader("Key Financial Findings")
    for item in insights["insights_text"]:
        st.markdown(f"- {item}")

    st.markdown("---")
    col_mom, col_dq = st.columns([1, 1])

    with col_mom:
        st.subheader("Month-over-Month Spending Velocity")
        mom_df = compute_month_over_month_trends(df_current)
        st.dataframe(mom_df[["month_year", "gross_expense", "refunds", "net_expense", "mom_spend_change", "mom_growth_pct"]], use_container_width=True)

    with col_dq:
        st.subheader("Data Quality & Hygiene Audit")
        dq_report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "data_quality_report.md")
        if os.path.exists(dq_report_path):
            with open(dq_report_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("Run `python -m python.run_pipeline` to generate data quality audit.")


# ==============================================================================
# PAGE 7: ORACLE SQL & SCHEMA VIEWER
# ==============================================================================
elif nav_selection == "🏛️ Oracle SQL & Schema":
    st.title("Oracle SQL & PL/SQL Database Architecture")
    st.markdown("Enterprise normalized schema design (3NF) and PL/SQL budget validation engine.")

    diag_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "diagrams", "database_schema.png")
    if os.path.exists(diag_path):
        st.image(diag_path, caption="Oracle 3NF Relational Model & Power BI Star-Schema Architecture", use_container_width=True)

    st.markdown("### Oracle Database Integration Scripts")
    sql_tab1, sql_tab2, sql_tab3, sql_tab4 = st.tabs([
        "01 DDL Tables", "03 Analytical Queries", "04 Views", "05 PL/SQL Budget Validation"
    ])

    base_dir = os.path.dirname(os.path.dirname(__file__))
    with sql_tab1:
        p = os.path.join(base_dir, "oracle_sql", "01_create_tables.sql")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                st.code(f.read(), language="sql")

    with sql_tab2:
        p = os.path.join(base_dir, "oracle_sql", "03_queries.sql")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                st.code(f.read(), language="sql")

    with sql_tab3:
        p = os.path.join(base_dir, "oracle_sql", "04_views.sql")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                st.code(f.read(), language="sql")

    with sql_tab4:
        p = os.path.join(base_dir, "oracle_sql", "05_plsql_budget_validation.sql")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                st.code(f.read(), language="sql")
