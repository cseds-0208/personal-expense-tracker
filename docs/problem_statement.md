# Problem Statement: Personal Expense Tracker and Budget Dashboard

**Domain:** Banking & Financial Services  
**Project Category:** End-to-End Enterprise Data Analytics & Financial Intelligence  
**Training Alignment:** HCL Data Analyst Training Program  
**Author:** Senior Data Analytics & Engineering Team  

---

## 1. Executive Summary
In today's fast-paced digital economy, individuals manage multiple financial transaction streams across digital wallets, credit cards, UPI, net banking, and cash disbursements. Without a centralized, rigorous financial tracking system, individuals face significant personal finance risks:
- Discretionary overspending and lack of spending discipline.
- Delayed or absent detection of category budget breaches.
- Inconsistent tracking and misclassification of financial transactions.
- Obscured visibility into true savings rates and month-over-month expenditure trends.
- Erroneous accounting of financial refunds (often mistakenly counted as ordinary expenses or double-counted as income).

This project delivers an industry-grade, end-to-end financial analytics and budget monitoring ecosystem: **Personal Expense Tracker and Budget Dashboard**.

---

## 2. Business & Analytical Problem
Personal financial data exhibits several common data-quality challenges:
1. **Unstructured & Heterogeneous Transaction Records**: Transaction descriptions from banks and merchant gateways frequently lack standard metadata (e.g., `"AMZN_PAY_MUMBAI"`, `"SWIGGY_BLR_01"`).
2. **Data Hygiene Vulnerabilities**: CSV bank statements frequently contain duplicate debits, null date stamps, erroneous negative values, and ambiguous refund entries.
3. **Budget Governance Gaps**: Traditional spreadsheets lack enforceable relational constraints and automated server-side breach evaluation.
4. **Disjointed Reporting**: Raw transactional spreadsheets fail to provide executives and end-users with interactive, multidimensional insights (e.g., Pareto analysis of spending categories, burn-rate velocity, and month-over-month variances).

---

## 3. Solution Architecture & Objectives
To solve these challenges, this system implements a multi-tiered architecture:
1. **Data Ingestion & Hygiene Engine (Python / Pandas / NumPy)**:
   - Robust parsing of raw transaction CSV statements.
   - Comprehensive data quality auditing: identification of missing values, duplicate entries, invalid numeric ranges, and boundary date anomalies.
   - Rule-based auto-categorization with fallback to `"Uncategorised"` and support for manual taxonomy override.
   - Distinct, audit-compliant handling of refund entries to prevent expense inflation.
   - Generation of clean, standardized datasets and a formal Data Quality Report.

2. **Enterprise Relational Storage & Rules Engine (Oracle SQL & PL/SQL)**:
   - Normalized relational schema (3NF) ensuring referential integrity (`TRANSACTIONS`, `CATEGORIES`, `MONTHLY_BUDGET`, `AUDIT_LOG`).
   - Server-side PL/SQL procedures and functions to calculate category spending, reconcile net expenditures, and programmatically flag budget breaches.
   - Analytical SQL views for real-time reporting of monthly spending, category distribution, and budget variance.

3. **Executive BI & Visualization (Power BI & Streamlit)**:
   - Modern, fintech-grade Streamlit application for transaction recording, dynamic categorization, budget management, and operational KPI monitoring.
   - Executive-grade 4-page Power BI dashboard suite leveraging star-schema data modeling and specialized DAX measures for deep variance analysis, month-over-month trends, and budget burn-rate tracking.

---

## 4. Scope and Success Criteria
- **Dataset Scale**: Minimum 500+ realistic synthetic financial transactions spanning multiple months, incorporating varied payment channels, refunds, month-end boundary events, and edge cases.
- **Accuracy**: 100% mathematical reconciliation between Python pipeline outputs, Oracle SQL views, and Power BI DAX KPIs.
- **Data Integrity**: Zero silent data discards; all anomalies explicitly flagged in a structured audit log.
- **Reliability**: Fully tested with automated test suites verifying all 8 mandatory test cases.
