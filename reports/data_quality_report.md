# Data Quality & Hygiene Audit Report

**Generated:** 2026-11-21 21:28:25  
**Project:** Personal Expense Tracker and Budget Dashboard  
**Source File:** `data/raw/sample_expenses_raw.csv`  
**Output Target:** `data/processed/clean_transactions.csv`  

---

## 1. Executive Summary Metrics

| Metric | Count | Percentage |
|---|---|---|
| **Total Input Raw Records** | **611** | 100.0% |
| **Valid Clean Records Retained** | **602** | 98.53% |
| **Quarantined Invalid Records** | **9** | 1.47% |
| **Duplicate Records Detected** | **5** | 0.82% |
| **Missing / Null Value Rows** | **2** | 0.33% |
| **Uncategorised Transactions** | **12** | 1.99% |
| **Merchant Refund Reversals** | **12** | 1.99% |

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
- Ingested 611 raw records from source CSV.
- Completed initial data validation: 607 candidate records retained.
- Quarantined 2 records with duplicate transaction IDs.
- Quarantined 3 identical duplicate transaction rows.
- Pipeline complete. Valid: 602, Excluded: 9, Duplicates: 5, Uncategorised: 12, Refunds: 12.

## 4. Quarantined Records Audit Sample

| Row # | Reason | Details |
|---|---|---|
| 607 | Missing or null transaction_date | `{'transaction_id': 'TXN-ANOM-001', 'transaction_date': '', 'descriptio...` |
| 608 | Invalid non-positive amount: -350.0 | `{'transaction_id': 'TXN-ANOM-002', 'transaction_date': '2026-11-12', '...` |
| 609 | Unparseable numeric amount: 'INVALID_AMT' | `{'transaction_id': 'TXN-ANOM-003', 'transaction_date': '2026-11-14', '...` |
| 610 | Missing or empty description | `{'transaction_id': 'TXN-ANOM-004', 'transaction_date': '2026-11-20', '...` |
| 605 | Duplicate transaction_id: TXN-BND-002 | `{'transaction_id': 'TXN-BND-002', 'transaction_date': datetime.date(20...` |
| 606 | Duplicate transaction_id: TXN-BND-007 | `{'transaction_id': 'TXN-BND-007', 'transaction_date': datetime.date(20...` |
| 195 | Duplicate business entry (identical date, description, amount, payment method) | `{'transaction_id': 'TXN-REG-00196', 'transaction_date': datetime.date(...` |
| 381 | Duplicate business entry (identical date, description, amount, payment method) | `{'transaction_id': 'TXN-REG-00382', 'transaction_date': datetime.date(...` |
| 390 | Duplicate business entry (identical date, description, amount, payment method) | `{'transaction_id': 'TXN-REG-00391', 'transaction_date': datetime.date(...` |
