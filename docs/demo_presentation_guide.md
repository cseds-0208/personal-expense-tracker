# Demo Video Recording Guide & Presentation Script

**Project:** Personal Expense Tracker and Budget Dashboard  
**Audience:** HCL Data Analyst Training Evaluators, Faculty, & Industry Stakeholders  
**Recommended Recording Duration:** 5 to 7 Minutes  
**Tooling Recommended:** OBS Studio, Loom, or Microsoft Clipchamp  

---

## 1. Presentation Structure & Timeline

| Timestamp | Presentation Phase | On-Screen Visual | Key Script Talking Points |
|---|---|---|---|
| **00:00 - 00:45** | **Introduction & Problem Statement** | Title Slide / `README.md` | Background, financial risks of unmonitored spending, business challenge. |
| **00:45 - 01:45** | **Architecture & Data Hygiene Pipeline** | Terminal & `reports/data_quality_report.md` | 500+ transaction ingestion, 0 silent discard policy, refund isolation. |
| **01:45 - 02:45** | **Oracle Database & PL/SQL Engine** | VS Code / SQL Developer (`01_create_tables.sql` & `05_plsql_budget_validation.sql`) | 3NF normalized schema, referential integrity, PL/SQL package for breach detection. |
| **02:45 - 04:30** | **Live Streamlit Application Walkthrough** | Streamlit Browser Window | KPI cards, add/edit/delete expense, auto-categorization test, budget management. |
| **04:30 - 05:45** | **Power BI Analytical Suite** | Power BI Desktop or `powerbi/dashboard_guide.md` | Star schema, DAX measures, 4-page interactive dashboard, slicers. |
| **05:45 - 06:30** | **Automated Testing & Conclusion** | Terminal `pytest` output (8/8 Passed) | Mathematical reconciliation, quality attestation, viva-voce readiness. |

---

## 2. Spoken Presentation Script

### 2.1 Opening (00:00 - 00:45)
> "Good day everyone. My name is [Your Name], and today I am pleased to present my capstone project for the HCL Data Analyst Training Program: the **Personal Expense Tracker and Budget Dashboard**.
> 
> In personal finance, individuals often lose track of discretionary spending due to fragmented payment channels—UPI, cards, net banking—and inconsistent transaction recording. The objective of this project is to create an end-to-end data analytics and business intelligence solution that ingests raw financial transactions, cleans and categorizes them, enforces relational integrity and budget limits using Oracle SQL and PL/SQL, and delivers actionable visual intelligence through Streamlit and Power BI."

### 2.2 Data Pipeline & Data Hygiene (00:45 - 01:45)
> "Let's begin with our Python data pipeline. We synthesized over 600 realistic transactions across Q4 2026. Rather than assuming clean data, we implemented a strict 'Zero Silent Discard' hygiene engine.
> 
> As seen in our Data Quality Report, the pipeline audited input records, quarantined exact duplicates, intercepted malformed amounts, and parsed edge cases such as month-end boundary transactions. Crucially, merchant refunds were identified and isolated so they properly offset category expenditures without inflating gross spending or distorting income."

### 2.3 Oracle Relational Database & PL/SQL (01:45 - 02:45)
> "Next, our storage and rules engine is built on enterprise Oracle SQL. We designed a 3NF normalized architecture comprising `TRANSACTIONS`, `CATEGORIES`, `PAYMENT_METHODS`, `MONTHLY_BUDGET`, and `BUDGET_BREACH_LOG`.
> 
> To enforce server-side budget governance, we created a specialized PL/SQL package: `PKG_BUDGET_MANAGEMENT`. It calculates net spending, evaluates category spending ceilings, and autonomously records breaches with status flags `BREACH`, `WARNING`, and `ON TRACK`."

### 2.4 Live Application Demo (02:45 - 04:30)
> "Now let's look at the interactive Streamlit application. On the **Dashboard Overview**, we observe high-level KPI cards displaying Monthly Income, Net Expenses, Remaining Surplus, and our Personal Savings Rate. Notice the dynamic alert banner immediately flagging categories that have breached their budget.
> 
> Under **Expense Management**, users can seamlessly record new transactions, search using keyword filters, or edit existing records.
> 
> In **Automatic Categorization**, our NLP rule engine automatically classifies vendor strings. Notice that unidentifiable transactions are responsibly assigned the status 'Uncategorised'—allowing users to perform manual category overrides without data distortion.
> 
> In **Budget Management**, spending caps can be adjusted on the fly, with immediate recalculation of utilization percentages."

### 2.5 Power BI Suite & DAX (04:30 - 05:45)
> "For executive-level analysis, we designed a complete Power BI dimensional star-schema. Supported by our custom DAX measure library, the Power BI dashboard includes 4 specialized pages:
> 1. Financial Overview
> 2. Expense Deep-Dive Analysis
> 3. Budget Monitoring & Governance
> 4. Strategic Financial Insights & Month-over-Month Velocity."

### 2.6 Testing & Conclusion (05:45 - 06:30)
> "Finally, software quality is guaranteed through our automated test suite. Running `pytest` verifies all 8 mandatory test cases—including uncategorised expense retention, refund handling, boundary dates, and full financial reconciliation across Python and SQL. All 8 tests pass with 100% precision.
> 
> Thank you for your time, and I welcome any questions regarding the implementation."

---

## 3. High-Frequency Viva Voce Q&A Preparation

**Q1: Why did you separate refunds instead of treating them as negative expenses or income?**  
*Answer:* Treating refunds as income artificially inflates gross revenue and distorts the personal savings rate. Treating them as ordinary positive expenses doubles the apparent spending error. Modeling refunds as a distinct transaction type allows clean calculation of Gross Outflow, Merchant Reimbursements, and Net Expenses.

**Q2: How does Oracle PL/SQL handle concurrent budget evaluation without slowing user transactions?**  
*Answer:* In `PKG_BUDGET_MANAGEMENT`, the breach logging procedure utilizes `PRAGMA AUTONOMOUS_TRANSACTION`. This decouples the audit log write from the primary transaction commit, ensuring audit durability without blocking user operations.

**Q3: How is the Star Schema structured in Power BI?**  
*Answer:* The central fact table is `Transactions`, joined via 1-to-Many relationships to three single-direction dimension tables: `Dim_Date`, `Dim_Categories`, and `Dim_Payment_Methods`, with `Monthly_Budget` functioning as a secondary budget target table.
