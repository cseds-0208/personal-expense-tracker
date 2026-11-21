# Project Documentation: Personal Expense Tracker & Budget Dashboard

## 1. System Overview & Architecture
The **Personal Expense Tracker and Budget Dashboard** is an enterprise data analytics capstone project developed under the HCL Data Analyst Training framework. It incorporates a modern multi-tiered architecture:

```
+-----------------------------------------------------------------------------------+
|                            RAW DATA SOURCES & INGESTION                           |
|      - Synthetic / Production CSV Transaction Statements (500+ records)           |
|      - Bank / Payment Gateway Logs (UPI, Credit Card, Net Banking, Cash)          |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                       PYTHON DATA HYGIENE & PREPROCESSING                         |
|   - Null & Invalid Data Auditing (Dates, Amounts, Types)                          |
|   - Duplicate Detection & Quarantine                                              |
|   - Rule-Based Keyword Auto-Categorization (Fallback: 'Uncategorised')            |
|   - Isolated Refund Handling & Offset Logic                                       |
|   - Data Quality Report & Audit Log Generation                                    |
+--------------------+------------------------------------+-------------------------+
                     |                                    |
                     v                                    v
+------------------------------------+   +------------------------------------------+
|      ORACLE SQL & PL/SQL ENGINE    |   |           POWER BI ANALYTICS SUITE       |
|  - 3NF Normalized Relational Model |   |  - Star Schema Analytical Model          |
|  - Relational Integrity (PK/FK/UQ) |   |  - 4 Executive Dashboard Views           |
|  - PL/SQL Validation Procedures    |   |  - Dynamic DAX Measures & Slicers        |
|  - Breach Detection & Logging      |   |  - Month-over-Month & Pareto Insights    |
|  - Reporting Views & CTE Queries   |   +------------------------------------------+
+--------------------+---------------+
                     |
                     v
+-----------------------------------------------------------------------------------+
|                        FINTECH STREAMLIT WEB APPLICATION                          |
|  - Executive KPI Cards & Visual Overview                                          |
|  - Transaction Management (CRUD, Search, Filters, Payment Methods)                |
|  - Dynamic Budget Allocation & Real-Time Breach Notification                      |
|  - Analytics & Data Quality Inspection Hub                                        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Directory Layout & Module Responsibilities

- **`app/`**: Interactive Streamlit web application.
  - `main.py`: Entry point for application dashboard, multi-page routing, and state orchestration.
  - `components/`: Modular UI widgets (KPI metrics, chart builders, modal dialogues, alert banners).
  - `styles/`: CSS styling adhering to fintech banking palettes.
- **`python/`**: Core data analytics, cleaning, categorization, and validation engine.
  - `data_cleaning.py`: Systematic ingestion, sanitation, deduplication, and refund isolation.
  - `expense_categorization.py`: Taxonomy engine with keyword rule mapping and taxonomy overrides.
  - `data_validation.py`: Data quality rule verification, schema validation, and audit compilation.
  - `analysis.py`: Analytical aggregations, burn rate, variance calculation, and insight generation.
- **`data/`**: Data assets.
  - `raw/`: Unsanitized raw CSV transaction statements.
  - `processed/`: Validated, cleaned, and categorized data ready for Oracle SQL and Power BI.
  - `sample_expenses.csv`: Benchmark 500+ record transaction dataset.
- **`oracle_sql/`**: Complete enterprise database scripts.
  - `01_create_tables.sql`: DDL for normalized tables, constraints, sequences, and indexes.
  - `02_insert_data.sql`: DML scripts populating categories, payment methods, budgets, and transactions.
  - `03_queries.sql`: Analytical queries, aggregations, window functions, and month-over-month comparisons.
  - `04_views.sql`: Reusable views for monthly spending, category breakdown, and budget utilization.
  - `05_plsql_budget_validation.sql`: PL/SQL stored procedures, functions, packages, and breach triggers.
- **`powerbi/`**: Power BI business intelligence assets.
  - `dax_measures.md`: Comprehensive library of DAX formulas.
  - `data_model.md`: Star schema layout, relationship cardinalities, and dimension attributes.
  - `dashboard_guide.md`: Step-by-step assembly guide for all 4 dashboard pages.
- **`diagrams/`**: Visual database architecture and star schema diagrams.
- **`reports/`**: Formal project documentation.
  - `data_quality_report.md`: Ingestion audit, invalid record handling, and cleaning summary.
  - `test_cases.md`: Test plan and execution outcomes across 8 mandatory test cases.
  - `insights_summary.md`: Strategic financial insights and spending recommendations.
- **`tests/`**: Automated verification test suite.
  - `test_project.py`: Pytest suite verifying all 8 test cases and data reconciliation.
