# Key Performance Indicator (KPI) Definitions

**Project:** Personal Expense Tracker and Budget Dashboard  
**Domain:** Personal Banking, Budgeting, & Wealth Analytics  
**Alignment:** HCL Data Analyst Enterprise Standards  

---

## 1. Overview
This document formally defines the mathematical formulas, business logic, data types, and calculation boundaries for all financial metrics and KPIs utilized across the Python analytics pipeline, Oracle SQL/PLSQL views, and Power BI dashboards.

---

## 2. Core Financial KPIs

### 2.1 Total Monthly Income ($I_m$)
- **Definition:** The sum of all credited revenue transactions within a specified calendar month ($m$).
- **Inclusion Criteria:** `TRANSACTION_TYPE = 'INCOME'` and valid positive amount.
- **Formula:**
  $$I_m = \sum_{t \in T_{income, m}} \text{Amount}_t$$
- **Business Rule:** Income is strictly segregated from expenses and is never included in expense calculations or budget depletion.

### 2.2 Total Monthly Gross Expenses ($E_{gross, m}$)
- **Definition:** The sum of all direct debit purchases and payments within month $m$.
- **Inclusion Criteria:** `TRANSACTION_TYPE = 'EXPENSE'` and valid positive amount.
- **Formula:**
  $$E_{gross, m} = \sum_{t \in T_{expense, m}} \text{Amount}_t$$

### 2.3 Total Monthly Refunds ($R_m$)
- **Definition:** The sum of all transaction reversals or merchant reimbursements received within month $m$.
- **Inclusion Criteria:** `TRANSACTION_TYPE = 'REFUND'` (or flagged as refund).
- **Formula:**
  $$R_m = \sum_{t \in T_{refund, m}} \text{Amount}_t$$
- **Business Rule:** A refund is a credit adjustment that offsets spending in its associated category. It must **never** be treated as primary income, nor as a positive expense.

### 2.4 Net Monthly Expenses ($E_{net, m}$)
- **Definition:** The true outlay incurred during month $m$, adjusted for returned merchandise and transaction reversals.
- **Formula:**
  $$E_{net, m} = E_{gross, m} - R_m$$

### 2.5 Net Monthly Savings ($S_m$) and Savings Rate ($SR_m$)
- **Definition:** The net surplus retained from income after meeting all living costs and discretionary expenditures.
- **Formulas:**
  $$S_m = I_m - E_{net, m}$$
  $$SR_m = \begin{cases} \left(\frac{S_m}{I_m}\right) \times 100\% & \text{if } I_m > 0 \\ 0\% & \text{otherwise} \end{cases}$$

---

## 3. Budget & Variance KPIs

### 3.1 Category Allocated Budget ($B_{c, m}$)
- **Definition:** The approved spending ceiling assigned to category $c$ for calendar month $m$.
- **Constraint:** Must be a non-negative numeric value ($B_{c, m} \ge 0$).

### 3.2 Category Budget Utilization ($BU_{c, m}$)
- **Definition:** The proportion of the allocated category budget consumed by net expenses.
- **Formula:**
  $$BU_{c, m} = \begin{cases} \left(\frac{E_{net, c, m}}{B_{c, m}}\right) \times 100\% & \text{if } B_{c, m} > 0 \\ 0\% & \text{otherwise} \end{cases}$$

### 3.3 Budget Variance ($V_{c, m}$)
- **Definition:** The monetary difference between the budgeted ceiling and actual net expenditure.
- **Formula:**
  $$V_{c, m} = B_{c, m} - E_{net, c, m}$$
  - $V_{c, m} > 0$: Favorable variance (Under budget / Surplus remaining).
  - $V_{c, m} = 0$: Balanced.
  - $V_{c, m} < 0$: Unfavorable variance (Over budget / Deficit).

### 3.4 Budget Breach Status
- **Business Logic Classification:**
  - **`BREACH` (Red Alert):** $E_{net, c, m} > B_{c, m}$ ($BU_{c, m} > 100\%$)
  - **`WARNING / NEAR BREACH` (Amber Alert):** $85\% \le BU_{c, m} \le 100\%$
  - **`ON TRACK` (Green):** $BU_{c, m} < 85\%$
  - **`NO BUDGET` (Neutral Grey):** When no budget is configured ($B_{c, m} = 0$ or null).

---

## 4. Trend & Operational Velocity KPIs

### 4.1 Average Daily Expenditure (Burn Rate) ($ADR_m$)
- **Formula:**
  $$ADR_m = \frac{E_{net, m}}{N_d}$$
  *(where $N_d$ is the count of calendar days elapsed or in month $m$)*

### 4.2 Month-over-Month (MoM) Spend Growth Rate ($MoM_m$)
- **Formula:**
  $$MoM_m = \left(\frac{E_{net, m} - E_{net, m-1}}{E_{net, m-1}}\right) \times 100\%$$

### 4.3 Category Spending Share ($CSS_{c, m}$)
- **Formula:**
  $$CSS_{c, m} = \left(\frac{E_{net, c, m}}{E_{net, m}}\right) \times 100\%$$
