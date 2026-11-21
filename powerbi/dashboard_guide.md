# Power BI Dashboard Assembly & Configuration Guide

**Project:** Personal Expense Tracker and Budget Dashboard  
**Author:** Senior BI Developer & Data Analyst Team  
**Dataset Path:** `data/processed/*.csv` or Direct Oracle Database Connection  

---

## 1. Environment & Setup Instructions

### Step 1: Open Power BI Desktop and Ingest Processed Data
1. Launch **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV** (or select **Oracle Database** if your local Oracle instance is active).
3. Import the following 4 files from `data/processed/`:
   - `clean_transactions.csv` (Name table as `Transactions`)
   - `categories.csv` (Name table as `Dim_Categories`)
   - `dim_date.csv` (Name table as `Dim_Date`)
   - `dim_payment_methods.csv` (Name table as `Dim_Payment_Methods`)
   - `monthly_budget.csv` (Name table as `Monthly_Budget`)
4. In Power Query, verify column types:
   - `amount` and `budget_amount` -> **Decimal Number / Currency**.
   - `transaction_date` and `date` -> **Date**.
   - `month`, `year`, `day` -> **Whole Number**.
5. Click **Close & Apply**.

### Step 2: Establish Model Relationships (Model View)
Navigate to the **Model View** tab and confirm or create the following 1-to-Many relationships:
1. `Dim_Date[date]` (1) -> `Transactions[transaction_date]` (*)
2. `Dim_Categories[category_name]` (1) -> `Transactions[category]` (*)
3. `Dim_Categories[category_name]` (1) -> `Monthly_Budget[category_name]` (*)
4. `Dim_Payment_Methods[method_name]` (1) -> `Transactions[payment_method]` (*)
5. Right-click `Dim_Date` -> Select **Mark as Date Table** -> Select `date` column.

### Step 3: Create the DAX Measures Table
1. In Home ribbon, click **Enter Data** -> Name the table `_Measures`.
2. Add all measures documented in `powerbi/dax_measures.md` (Total Income, Net Expenses, Net Savings, Savings Rate %, Budget Utilization %, etc.).

---

## 2. Dashboard Pages Specification

### Page 1: Financial Overview (Executive Command Center)
- **Global Header**: Text box or card bound to `[Dashboard Title]`.
- **Top Slicers Panel**:
  - Horizontal Tile Slicer: `Dim_Date[month_year]`
  - Dropdown Slicer: `Dim_Categories[category_name]`
  - Dropdown Slicer: `Transactions[payment_method]`
- **Row 1 - KPI Cards (5 Cards)**:
  1. **Total Income**: Measure `[Total Income]`, callout value `#10B981` (Green).
  2. **Net Expenses**: Measure `[Net Expenses]`, callout value `#EF4444` (Red).
  3. **Net Savings**: Measure `[Net Savings]`, callout value `#38BDF8` (Sky Blue).
  4. **Savings Rate %**: Measure `[Savings Rate %]`, callout value `#3B82F6` (Blue).
  5. **Budget Utilization %**: Measure `[Budget Utilization %]`, callout value conditional formatting based on `[Budget Status Color]`.
- **Row 2 - Visualizations**:
  - **Left (60% width)**: Clustered Column Chart
    - *X-Axis*: `Dim_Date[month_year]`
    - *Y-Axis*: `[Total Income]`, `[Net Expenses]`, `[Net Savings]`
    - *Colors*: Income (Emerald), Expenses (Rose), Savings (Cyan).
  - **Right (40% width)**: Donut Chart
    - *Legend*: `Dim_Categories[category_name]`
    - *Values*: `[Net Expenses]`
- **Row 3**: Summary Grid Table displaying `[Month]`, `[Income]`, `[Gross Expenses]`, `[Refunds]`, `[Net Expenses]`, `[Savings]`, and `[Savings Rate %]`.

---

### Page 2: Expense Analysis (Deep-Dive Outlay Diagnostics)
- **Visual 1 (Top Left)**: Donut / Pie Chart:
  - *Legend*: `Dim_Categories[category_name]`
  - *Values*: `[Net Expenses]`
  - *Data Labels*: Category name + Percentage of total.
- **Visual 2 (Top Right)**: Line and Clustered Column Chart (Monthly Expense Trend & Velocity):
  - *X-Axis*: `Dim_Date[month_year]` (or Day date drill-down)
  - *Column Y-Axis*: `[Gross Expenses]`
  - *Line Y-Axis*: `[Net Expenses]`
  - *Secondary Line*: `[Daily Burn Rate]`
- **Visual 3 (Bottom Left)**: Bar Chart (Payment Method Breakdown):
  - *Y-Axis*: `Dim_Payment_Methods[method_name]`
  - *X-Axis*: `[Net Expenses]`
  - *Data Labels*: Inside end, formatted currency.
- **Visual 4 (Bottom Right)**: Treemap / Matrix:
  - *Category Level*: `Dim_Categories[category_name]` -> `Transactions[description]` (Drill-down enabled)
  - *Values*: `[Net Expenses]`, `[Total Transactions]`

---

### Page 3: Budget Monitoring & Breach Governance
- **Header Alert Banner**: Multi-row card showing `[Breached Category Count]` and warning status.
- **Visual 1 (Top Center)**: Clustered Bar Chart (Budget vs Actual Net Spend):
  - *Y-Axis*: `Dim_Categories[category_name]`
  - *X-Axis*: `[Allocated Budget]`, `[Net Expenses]`
  - *Color Bar*: Budget (Steel Grey `#94A3B8`), Net Spend (Coral `#F43F5E`).
- **Visual 2 (Right Side)**: Gauge / Radial Chart:
  - *Value*: `[Budget Utilization %]`
  - *Target*: `100%`
  - *Min/Max*: `0%` to `150%`
  - *Color*: Dynamic based on `[Budget Status Color]`.
- **Visual 3 (Bottom)**: Detailed Budget Governance Table:
  - *Columns*:
    1. `Category Name`
    2. `Allocated Budget (₹)`
    3. `Gross Outlay (₹)`
    4. `Refunds Offset (₹)`
    5. `Net Actual Outlay (₹)`
    6. `Budget Variance (₹)`
    7. `Utilization %`
    8. `Status Flag` (`BREACH`, `WARNING`, `ON TRACK`)
  - *Conditional Formatting*: Background color of `Status Flag` set to `[Budget Status Color]`.

---

### Page 4: Financial Insights & Strategic Analytics
- **Visual 1**: Ranked Bar Chart (Pareto Spending - Top Outflow Centers).
- **Visual 2**: Waterfall Chart (Month-over-Month Variance Walk):
  - *Category*: `Dim_Date[month_year]`
  - *Breakdown*: `Dim_Categories[category_name]`
  - *Y-Axis*: `[MoM Spend Change]`
- **Visual 3**: Scatter Plot / Matrix (Transaction Velocity vs Average Ticket Size):
  - *X-Axis*: `[Total Transactions]`
  - *Y-Axis*: `[Average Ticket Size]`
  - *Size*: `[Net Expenses]`
- **Visual 4**: Strategic Analytical Findings Card:
  - Text summary highlighting: Highest spending category, Lowest spending category, Personal Savings Rate, and Actionable financial discipline recommendations.
