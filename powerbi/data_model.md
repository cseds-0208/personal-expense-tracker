# Power BI Analytical Data Model (Star Schema)

**Project:** Personal Expense Tracker and Budget Dashboard  
**Domain:** Personal Financial Management & BI Analytics  
**Architecture:** Kimball Dimensional Star Schema  

---

## 1. Dimensional Architecture Overview

To provide maximum query performance, flexible slicer filtering, and clean DAX calculations, the analytical model implements a Kimball-style **Star Schema**:

```
                  +-------------------------+
                  |        Dim_Date         |
                  |-------------------------|
                  | Date (PK)               |
                  | Year, Quarter, Month    |
                  | Month_Year, Day, DayName|
                  | Is_Weekend, Is_Month_End|
                  +------------+------------+
                               | 1
                               | 
                               | *
+-----------------------+      |      +--------------------------+
|    Dim_Categories     |      |      |   Dim_Payment_Methods    |
|-----------------------|      |      |--------------------------|
| Category_ID (PK)      |      |      | Payment_Method_ID (PK)   |
| Category_Name (UQ)    +---+  |  +---+ Method_Name (UQ)         |
| Category_Type         |   |  |  |   | Channel_Type             |
+-----------+-----------+   |  |  |   +--------------------------+
            | 1             |  |  |
            |               |  |  |
            | *             v  v  v
+-----------+-----------+ +--------------------------------------+
|    Monthly_Budget     | |            Transactions              |
|-----------------------| |--------------------------------------|
| Budget_ID (PK)        | | Transaction_ID (PK)                  |
| Category_ID (FK)      | | Transaction_Date (FK)                |
| Budget_Month          | | Description                          |
| Budget_Year           | | Amount                               |
| Budget_Amount         | | Category_ID (FK)                     |
+-----------------------+ | Transaction_Type (INCOME/EXPENSE)    |
                          | Payment_Method (FK)                  |
                          | Notes, Source_Raw_ID                 |
                          +--------------------------------------+
```

---

## 2. Table Specifications & Cardinalities

### 2.1 Fact Table: `Transactions`
- **Source:** `data/processed/clean_transactions.csv` (or Oracle `TRANSACTIONS` table)
- **Granularity:** One row per individual financial transaction.
- **Attributes:**
  - `transaction_id` (Text / Integer) — Primary Key
  - `transaction_date` (Date) — Foreign key to `Dim_Date[Date]`
  - `description` (Text) — Vendor or description label
  - `amount` (Decimal) — Positive monetary value
  - `category` / `category_id` (Integer) — Foreign key to `Dim_Categories[Category_ID]`
  - `transaction_type` (Text) — `INCOME`, `EXPENSE`, or `REFUND`
  - `payment_method` (Text) — Foreign key to `Dim_Payment_Methods[Method_Name]`
  - `notes` (Text) — User notes / remarks

### 2.2 Dimension: `Dim_Categories`
- **Source:** `data/processed/categories.csv`
- **Granularity:** One row per unique category.
- **Relationship:** `Dim_Categories[Category_Name]` (1) to `Transactions[Category]` (*) with Single cross-filter direction.

### 2.3 Dimension: `Dim_Date`
- **Source:** `data/processed/dim_date.csv`
- **Granularity:** One row per calendar date from `2026-10-01` to `2026-12-31`.
- **Relationship:** `Dim_Date[Date]` (1) to `Transactions[Transaction_Date]` (*) with Single cross-filter direction.
- **Mark as Date Table:** Yes (in Power BI Desktop).

### 2.4 Dimension: `Dim_Payment_Methods`
- **Source:** `data/processed/dim_payment_methods.csv`
- **Granularity:** One row per payment channel (`Net Banking`, `UPI`, `Credit Card`, `Debit Card`, `Cash`, `Other`).
- **Relationship:** `Dim_Payment_Methods[Method_Name]` (1) to `Transactions[Payment_Method]` (*).

### 2.5 Secondary Fact / Budget Target Table: `Monthly_Budget`
- **Source:** `data/processed/monthly_budget.csv`
- **Granularity:** One row per category per calendar month.
- **Attributes:** `budget_id`, `category_id`, `category_name`, `budget_month`, `budget_year`, `budget_amount`.
- **Relationship:** `Dim_Categories[Category_Name]` (1) to `Monthly_Budget[Category_Name]` (*).

---

## 3. Recommended Column Formatting in Power BI
- Currency fields (`amount`, `budget_amount`): Format as `Currency` -> `₹ English (India)`.
- Dates (`transaction_date`, `Date`): Format as `Short Date` (`YYYY-MM-DD`).
- Sort Orders:
  - Sort `Dim_Date[Month_Name]` by `Dim_Date[Month]`.
  - Sort `Dim_Date[Day_Name]` by `Dim_Date[Day]`.
