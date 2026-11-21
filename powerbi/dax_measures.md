# Power BI DAX Measures Library

**Project:** Personal Expense Tracker and Budget Dashboard  
**Domain:** Personal Banking & Enterprise Wealth Analytics  
**Training Alignment:** HCL Data Analyst Enterprise Standards  

---

## 1. Core Financial Measures (Base Aggregations)

### Total Income
```dax
Total Income = 
CALCULATE(
    SUM(Transactions[amount]),
    Transactions[transaction_type] = "INCOME"
)
```
*Format: Currency `₹#,##0.00` | Excludes all debit and refund records.*

### Gross Expenses
```dax
Gross Expenses = 
CALCULATE(
    SUM(Transactions[amount]),
    Transactions[transaction_type] = "EXPENSE"
)
```
*Format: Currency `₹#,##0.00` | Strict gross outlays before refund offsets.*

### Total Refunds
```dax
Total Refunds = 
CALCULATE(
    SUM(Transactions[amount]),
    Transactions[transaction_type] = "REFUND"
)
```
*Format: Currency `₹#,##0.00` | Merchant reversals and credits.*

### Net Expenses
```dax
Net Expenses = 
MAX(0, [Gross Expenses] - [Total Refunds])
```
*Format: Currency `₹#,##0.00` | True net expenditure after contra-expense refund adjustments.*

### Net Savings
```dax
Net Savings = 
[Total Income] - [Net Expenses]
```
*Format: Currency `₹#,##0.00` | Retained financial surplus.*

### Savings Rate %
```dax
Savings Rate % = 
DIVIDE(
    [Net Savings],
    [Total Income],
    0.00
)
```
*Format: Percentage `0.0%` | Financial capital retention efficiency.*

---

## 2. Budget Monitoring & Breach Detection Measures

### Allocated Budget
```dax
Allocated Budget = 
SUM(Monthly_Budget[budget_amount])
```

### Budget Variance
```dax
Budget Variance = 
[Allocated Budget] - [Net Expenses]
```
*Interpretation: Positive indicates favorable surplus; negative indicates budget deficit.*

### Budget Utilization %
```dax
Budget Utilization % = 
DIVIDE(
    [Net Expenses],
    [Allocated Budget],
    0.00
)
```
*Format: Percentage `0.0%`.*

### Budget Status Flag
```dax
Budget Status = 
SWITCH(
    TRUE(),
    ISBLANK([Allocated Budget]) || [Allocated Budget] = 0, "No Budget",
    [Net Expenses] > [Allocated Budget], "BREACH",
    [Budget Utilization %] >= 0.85, "WARNING",
    "ON TRACK"
)
```

### Budget Status Color (Conditional Formatting)
```dax
Budget Status Color = 
SWITCH(
    [Budget Status],
    "BREACH", "#EF4444",    // Bright Red
    "WARNING", "#F59E0B",   // Amber
    "ON TRACK", "#10B981",  // Emerald Green
    "#64748B"               // Slate Grey
)
```

### Count of Breached Categories
```dax
Breached Category Count = 
COUNTROWS(
    FILTER(
        VALUES(Dim_Categories[category_name]),
        [Net Expenses] > [Allocated Budget] && [Allocated Budget] > 0
    )
)
```

---

## 3. Trend & Month-over-Month (MoM) Measures

### Prior Month Net Expenses
```dax
Prior Month Net Expenses = 
CALCULATE(
    [Net Expenses],
    DATEADD(Dim_Date[date], -1, MONTH)
)
```

### MoM Spend Change
```dax
MoM Spend Change = 
IF(
    ISBLANK([Prior Month Net Expenses]),
    BLANK(),
    [Net Expenses] - [Prior Month Net Expenses]
)
```

### MoM Spend Growth %
```dax
MoM Spend Growth % = 
DIVIDE(
    [MoM Spend Change],
    [Prior Month Net Expenses],
    BLANK()
)
```
*Format: Percentage `+0.0%;-0.0%;0.0%`.*

### Daily Burn Rate (Average Daily Spend)
```dax
Daily Burn Rate = 
DIVIDE(
    [Net Expenses],
    DISTINCTCOUNT(Dim_Date[date]),
    0.00
)
```

---

## 4. Operational & Dynamic KPI Title Measures

### Transaction Count
```dax
Total Transactions = COUNTROWS(Transactions)
```

### Uncategorised Expense Count
```dax
Uncategorised Count = 
CALCULATE(
    COUNTROWS(Transactions),
    Dim_Categories[category_name] = "Uncategorised"
)
```

### Dynamic Dashboard Header
```dax
Dashboard Title = 
VAR SelectedMonth = SELECTEDVALUE(Dim_Date[month_name], "All Months")
VAR SelectedYear = SELECTEDVALUE(Dim_Date[year], "All Years")
RETURN "Personal Wealth & Expense Command Center | " & SelectedMonth & " " & SelectedYear
```
