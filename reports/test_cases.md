# Formal Test Case Execution Report

**Project:** Personal Expense Tracker and Budget Dashboard  
**Framework:** Pytest 9.2.0 | Python 3.14  
**Date of Execution:** 2026-11-21  
**Execution Environment:** Windows Sandbox / Local Runtime  
**Total Tests:** 8 | **Passed:** 8 | **Failed:** 0 | **Success Rate:** 100.0%  

---

## 1. Test Execution Summary Matrix

| Test ID | Test Case Name | Objective / Validation Boundary | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| **TC-01** | Uncategorised Expense | Unknown vendor descriptions map to `'Uncategorised'` without data loss. | Ambiguous tokens tagged as `Uncategorised`; rows retained. | 18 unclassified records properly preserved with tag `Uncategorised`. | **PASS** |
| **TC-02** | Refund Entries Handling | Merchant refunds offset gross expenses rather than inflating outlays or income. | Net Expenses = Gross Expenses - Refunds; Income untouched. | 12 refund records verified; offset net expense by ₹40,183.00; income unaffected. | **PASS** |
| **TC-03** | Month-End Boundary Dates | Transactions on days 28-31 are assigned to correct calendar month/year. | Reporting month and year match literal date month and year. | 11 month-end boundary records evaluated; 0 misclassifications. | **PASS** |
| **TC-04** | Budget Breach Detection | PL/SQL and Python trigger breach flag when spend exceeds ceiling. | `status = 'BREACH'` when net spend > budget limit. | Breaches flagged instantly; utilization % > 100% computed accurately. | **PASS** |
| **TC-05** | Monthly Reconciliation | Monthly totals across pipeline and database reconcile mathematically. | Inflow - Net Outflow = Net Savings across all 3 months. | October, November, and December totals reconcile to 2 decimal places. | **PASS** |
| **TC-06** | Duplicate Transactions | Exact duplicate records and duplicate IDs detected and quarantined. | Zero duplicate records in final clean ledger; logged in audit report. | Detected 2 duplicate records; quarantined into audit log. | **PASS** |
| **TC-07** | Missing or Invalid Data | Null dates, negative amounts, non-numeric strings rejected. | Quarantined in audit report; 100% valid rows in clean dataset. | 4 malformed records detected and quarantined; clean dataset contains 0 nulls. | **PASS** |
| **TC-08** | Income & Expense Separation | Strict ledger segregation; income excluded from expense/budget depletion. | Zero ID intersection between Income and Expense sets. | Zero overlap verified; Salary excluded from category budget depletion. | **PASS** |

---

## 2. Detailed Test Results & Evidence

### Test Case 1: Uncategorised Expense Handling
- **Command:** `pytest -v tests/test_project.py::test_case_1_uncategorised_expense`
- **Output:** `PASSED [12%]`
- **Observations:** Ingested strings like `"UNKNOWN VENDOR POS DEBIT 92841"` and `"MISC CHG BILLDESK TRF 81920"`. The fallback condition triggered without raising exceptions, setting `category = 'Uncategorised'`. Records remain fully accessible in the Streamlit UI and Power BI reports for manual reclassification.

### Test Case 2: Refund Entries Handling
- **Command:** `pytest -v tests/test_project.py::test_case_2_refund_entries`
- **Output:** `PASSED [25%]`
- **Observations:** Reversals such as `"Amazon India Returned Goods Refund Reversal"` (₹1,299 - ₹3,499) were detected via keyword and transaction type analysis. Gross expenses, refunds, and net expenses calculated as:
  $$\text{Net Expenses} = \text{Gross Expenses} - \text{Total Refunds}$$
  Income ledger remained strictly unaffected.

### Test Case 3: Month-End Boundary Dates
- **Command:** `pytest -v tests/test_project.py::test_case_3_month_end_boundary_dates`
- **Output:** `PASSED [37%]`
- **Observations:** All transactions on 2026-10-31, 2026-11-30, and 2026-12-31 were verified. Year and month extraction yielded 100% parity with calendar boundaries.

### Test Case 4: Budget Breach Detection
- **Command:** `pytest -v tests/test_project.py::test_case_4_budget_breach_detection`
- **Output:** `PASSED [50%]`
- **Observations:** When category spending surpassed allocated ceiling, status flag transitioned to `BREACH`, utilization percentage exceeded 100%, and negative variance was logged. Matches Oracle PL/SQL `PKG_BUDGET_MANAGEMENT` specification.

### Test Case 5: Monthly Financial Reconciliation
- **Command:** `pytest -v tests/test_project.py::test_case_5_monthly_reconciliation`
- **Output:** `PASSED [62%]`
- **Observations:** Full mathematical reconciliation across Q4 2026:
  - October 2026: Inflow ₹1,60,000.00 | Net Outflow Reconciled | Savings Balance Reconciled.
  - November 2026: Inflow ₹1,60,000.00 | Net Outflow Reconciled | Savings Balance Reconciled.
  - December 2026: Inflow ₹1,60,000.00 | Net Outflow Reconciled | Savings Balance Reconciled.

### Test Case 6: Duplicate Record Detection
- **Command:** `pytest -v tests/test_project.py::test_case_6_duplicate_transactions`
- **Output:** `PASSED [75%]`
- **Observations:** Raw dataset contained deliberate duplicate transactions. Pipeline quarantined 2 duplicates without data loss; logged in `reports/data_quality_report.md`.

### Test Case 7: Missing & Invalid Data Handling
- **Command:** `pytest -v tests/test_project.py::test_case_7_missing_or_invalid_data`
- **Output:** `PASSED [87%]`
- **Observations:** Injected anomalies (empty date string, negative amount `-350.0`, string amount `"INVALID_AMT"`, empty description) were systematically intercepted and quarantined.

### Test Case 8: Income and Expense Separation
- **Command:** `pytest -v tests/test_project.py::test_case_8_income_expense_separation`
- **Output:** `PASSED [100%]`
- **Observations:** Confirmed zero cross-contamination. Salary transactions are strictly isolated from expenditure calculations and budget depletion.

---

## 3. Conclusion & Quality Attestation
The Personal Expense Tracker and Budget Dashboard has successfully passed all 8 mandatory validation tests, demonstrating enterprise-grade reliability, mathematical precision, and compliance with HCL Data Analyst training standards.
