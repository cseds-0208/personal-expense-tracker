"""
UI Components & Visualizations for Streamlit
--------------------------------------------
Provides reusable Plotly charts, KPI widgets, and fintech components.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_kpi(title: str, value: str, subtext: str = "", delta_color: str = "#38bdf8", border_col: str = "#334155"):
    """Renders a fintech KPI metric card."""
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid {border_col};
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    ">
        <div style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em;">
            {title}
        </div>
        <div style="font-size: 1.7rem; font-weight: 700; color: {delta_color}; margin: 0.25rem 0;">
            {value}
        </div>
        <div style="font-size: 0.8rem; color: #64748b;">
            {subtext}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def plot_category_donut(df: pd.DataFrame) -> go.Figure:
    """Generates a category net expenditure donut chart."""
    expense_data = df[df["transaction_type"].isin(["EXPENSE", "REFUND"])]
    if expense_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No Expense Data Available", showarrow=False)
        return fig

    # Net spend per category
    cat_summary = expense_data.groupby("category").apply(
        lambda g: max(0.0, g[g["transaction_type"] == "EXPENSE"]["amount"].sum() - g[g["transaction_type"] == "REFUND"]["amount"].sum()),
        include_groups=False
    ).reset_index(name="net_spend")
    cat_summary = cat_summary[cat_summary["net_spend"] > 0].sort_values(by="net_spend", ascending=False)

    colors = px.colors.qualitative.Prism

    fig = go.Figure(data=[go.Pie(
        labels=cat_summary["category"],
        values=cat_summary["net_spend"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='#0f172a', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>Net Spend: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="<b>Category-Wise Expense Breakdown</b>",
        title_font=dict(size=15, color="#f8fafc"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(font=dict(color='#94a3b8', size=11), orientation="h", yanchor="bottom", y=-0.3),
        margin=dict(l=10, r=10, t=40, b=50),
        height=380
    )
    return fig


def plot_budget_vs_actual_chart(cat_budget_df: pd.DataFrame) -> go.Figure:
    """Creates a clustered bar chart of Budget vs Actual Net Spend."""
    df_plot = cat_budget_df.copy()
    df_plot = df_plot[df_plot["category"] != "Salary"]

    fig = go.Figure()

    # Allocated Budget bar
    fig.add_trace(go.Bar(
        x=df_plot["category"],
        y=df_plot["budget_amount"],
        name="Allocated Budget",
        marker_color="#64748b",
        hovertemplate='<b>%{x}</b><br>Budget: ₹%{y:,.2f}<extra></extra>'
    ))

    # Net Actual Spend bar with dynamic breach coloring
    colors = [
        '#ef4444' if st == 'BREACH' else ('#f59e0b' if st == 'WARNING' else '#10b981')
        for st in df_plot["status"]
    ]

    fig.add_trace(go.Bar(
        x=df_plot["category"],
        y=df_plot["net_spend"],
        name="Actual Net Spend",
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>Actual Spend: ₹%{y:,.2f}<br>Status: %{text}<extra></extra>',
        text=df_plot["status"]
    ))

    fig.update_layout(
        title="<b>Category Budget vs. Actual Net Outlay</b>",
        title_font=dict(size=15, color="#f8fafc"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155', tickangle=-30),
        yaxis=dict(gridcolor='#334155', title="Amount (INR ₹)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=50, b=50),
        height=400
    )
    return fig


def plot_monthly_trend_chart(mom_df: pd.DataFrame) -> go.Figure:
    """Creates a monthly spending trend line and bar chart."""
    if mom_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for monthly trend", showarrow=False)
        return fig

    fig = go.Figure()

    # Gross Expense Bar
    fig.add_trace(go.Bar(
        x=mom_df["month_year"],
        y=mom_df["gross_expense"],
        name="Gross Expenses",
        marker_color="#38bdf8",
        opacity=0.6,
        hovertemplate='Gross: ₹%{y:,.2f}<extra></extra>'
    ))

    # Net Expense Line
    fig.add_trace(go.Scatter(
        x=mom_df["month_year"],
        y=mom_df["net_expense"],
        name="Net Expenses (Refund Adjusted)",
        mode='lines+markers',
        line=dict(color="#f43f5e", width=3),
        marker=dict(size=8, color="#f43f5e"),
        hovertemplate='Net: ₹%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="<b>Monthly Spending Trend & Refund Reconciliations</b>",
        title_font=dict(size=15, color="#f8fafc"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155'),
        yaxis=dict(gridcolor='#334155', title="Amount (INR ₹)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=50, b=30),
        height=380
    )
    return fig


def plot_payment_methods_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing spending distribution across payment channels."""
    expense_data = df[df["transaction_type"] == "EXPENSE"]
    if expense_data.empty:
        fig = go.Figure()
        return fig

    pm_grp = expense_data.groupby("payment_method")["amount"].sum().reset_index()
    pm_grp = pm_grp.sort_values(by="amount", ascending=True)

    fig = go.Figure(go.Bar(
        x=pm_grp["amount"],
        y=pm_grp["payment_method"],
        orientation='h',
        marker_color='#818cf8',
        hovertemplate='<b>%{y}</b>: ₹%{x:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="<b>Expense Volume by Payment Rail</b>",
        title_font=dict(size=15, color="#f8fafc"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155', title="Volume (INR ₹)"),
        yaxis=dict(gridcolor='#334155'),
        margin=dict(l=10, r=10, t=40, b=20),
        height=320
    )
    return fig
