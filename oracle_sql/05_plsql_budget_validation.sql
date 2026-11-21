-- =============================================================================
-- SCRIPT 05: ORACLE PL/SQL BUDGET VALIDATION & BREACH DETECTION ENGINE
-- PROJECT: Personal Expense Tracker and Budget Dashboard
-- DOMAIN: Banking & Financial Services
-- ALIGNMENT: HCL Data Analyst Enterprise Training Standard
-- TARGET COMPATIBILITY: Oracle 12c / 18c / 19c / 21c / 23c / XE
-- =============================================================================

SET SERVEROUTPUT ON SIZE 1000000;
SET FEEDBACK ON;

-- -----------------------------------------------------------------------------
-- PACKAGE SPECIFICATION: PKG_BUDGET_MANAGEMENT
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PACKAGE PKG_BUDGET_MANAGEMENT AS
    -- Custom Exceptions
    e_invalid_month     EXCEPTION;
    e_category_not_found EXCEPTION;
    e_no_budget_set     EXCEPTION;

    -- Constants
    c_warning_threshold CONSTANT NUMBER := 85.0; -- 85% warning threshold

    -- Function to compute net spending for a category in a given month and year
    -- Incorporates gross expenses minus refunds (excludes income)
    FUNCTION fn_get_net_spending (
        p_category_id IN NUMBER,
        p_month       IN NUMBER,
        p_year        IN NUMBER
    ) RETURN NUMBER;

    -- Function to evaluate budget breach status
    -- Returns: 'BREACH', 'WARNING', 'ON_TRACK', or 'NO_BUDGET'
    FUNCTION fn_check_budget_breach (
        p_category_id      IN NUMBER,
        p_month            IN NUMBER,
        p_year             IN NUMBER,
        p_utilization_pct  OUT NUMBER,
        p_variance_amount  OUT NUMBER
    ) RETURN VARCHAR2;

    -- Procedure to batch-evaluate all categories for a given month/year and log breaches
    PROCEDURE pr_validate_monthly_budgets (
        p_month        IN NUMBER,
        p_year         IN NUMBER,
        o_breach_count OUT NUMBER
    );

    -- Autonomous procedure to log breach events into BUDGET_BREACH_LOG
    PROCEDURE pr_log_breach (
        p_category_id   IN NUMBER,
        p_month         IN NUMBER,
        p_year          IN NUMBER,
        p_budget_amount IN NUMBER,
        p_actual_spend  IN NUMBER,
        p_variance      IN NUMBER,
        p_status        IN VARCHAR2
    );

END PKG_BUDGET_MANAGEMENT;
/

-- -----------------------------------------------------------------------------
-- PACKAGE BODY: PKG_BUDGET_MANAGEMENT
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PACKAGE BODY PKG_BUDGET_MANAGEMENT AS

    -- Function Implementation: fn_get_net_spending
    FUNCTION fn_get_net_spending (
        p_category_id IN NUMBER,
        p_month       IN NUMBER,
        p_year        IN NUMBER
    ) RETURN NUMBER IS
        v_gross_expenses NUMBER(12,2) := 0;
        v_total_refunds  NUMBER(12,2) := 0;
        v_net_spending   NUMBER(12,2) := 0;
    BEGIN
        -- Validate month parameter
        IF p_month < 1 OR p_month > 12 THEN
            RAISE e_invalid_month;
        END IF;

        -- Sum gross expenses strictly for EXPENSE transaction type
        SELECT NVL(SUM(AMOUNT), 0)
        INTO v_gross_expenses
        FROM TRANSACTIONS
        WHERE CATEGORY_ID = p_category_id
          AND TRANSACTION_TYPE = 'EXPENSE'
          AND EXTRACT(MONTH FROM TRANSACTION_DATE) = p_month
          AND EXTRACT(YEAR FROM TRANSACTION_DATE) = p_year;

        -- Sum refunds for contra-expense offset
        SELECT NVL(SUM(AMOUNT), 0)
        INTO v_total_refunds
        FROM TRANSACTIONS
        WHERE CATEGORY_ID = p_category_id
          AND TRANSACTION_TYPE = 'REFUND'
          AND EXTRACT(MONTH FROM TRANSACTION_DATE) = p_month
          AND EXTRACT(YEAR FROM TRANSACTION_DATE) = p_year;

        -- Calculate net outlay (cannot drop below 0)
        v_net_spending := GREATEST(0, v_gross_expenses - v_total_refunds);

        RETURN v_net_spending;

    EXCEPTION
        WHEN e_invalid_month THEN
            DBMS_OUTPUT.PUT_LINE('ERROR: Invalid month ' || p_month || '. Must be between 1 and 12.');
            RETURN 0;
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('ERROR in fn_get_net_spending: ' || SQLERRM);
            RETURN 0;
    END fn_get_net_spending;


    -- Function Implementation: fn_check_budget_breach
    FUNCTION fn_check_budget_breach (
        p_category_id      IN NUMBER,
        p_month            IN NUMBER,
        p_year             IN NUMBER,
        p_utilization_pct  OUT NUMBER,
        p_variance_amount  OUT NUMBER
    ) RETURN VARCHAR2 IS
        v_budget_amount  NUMBER(12,2) := 0;
        v_net_spend      NUMBER(12,2) := 0;
        v_status         VARCHAR2(20);
    BEGIN
        -- Retrieve allocated budget for the period
        BEGIN
            SELECT BUDGET_AMOUNT
            INTO v_budget_amount
            FROM MONTHLY_BUDGET
            WHERE CATEGORY_ID = p_category_id
              AND BUDGET_MONTH = p_month
              AND BUDGET_YEAR = p_year;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                p_utilization_pct := 0;
                p_variance_amount := 0;
                RETURN 'NO_BUDGET';
        END;

        -- Retrieve net spending using our audited function
        v_net_spend := fn_get_net_spending(p_category_id, p_month, p_year);

        -- Calculate variance: Favorable (+) if under budget, Unfavorable (-) if breached
        p_variance_amount := v_budget_amount - v_net_spend;

        -- Calculate utilization %
        IF v_budget_amount > 0 THEN
            p_utilization_pct := ROUND((v_net_spend / v_budget_amount) * 100, 2);
        ELSE
            p_utilization_pct := 0;
        END IF;

        -- Evaluate breach status
        IF v_net_spend > v_budget_amount THEN
            v_status := 'BREACH';
        ELSIF p_utilization_pct >= c_warning_threshold THEN
            v_status := 'WARNING';
        ELSE
            v_status := 'ON_TRACK';
        END IF;

        RETURN v_status;

    EXCEPTION
        WHEN OTHERS THEN
            p_utilization_pct := 0;
            p_variance_amount := 0;
            RETURN 'ERROR';
    END fn_check_budget_breach;


    -- Procedure Implementation: pr_log_breach (Autonomous Transaction)
    PROCEDURE pr_log_breach (
        p_category_id   IN NUMBER,
        p_month         IN NUMBER,
        p_year          IN NUMBER,
        p_budget_amount IN NUMBER,
        p_actual_spend  IN NUMBER,
        p_variance      IN NUMBER,
        p_status        IN VARCHAR2
    ) IS
        PRAGMA AUTONOMOUS_TRANSACTION;
    BEGIN
        INSERT INTO BUDGET_BREACH_LOG (
            LOG_ID, CATEGORY_ID, LOG_MONTH, LOG_YEAR,
            BUDGET_AMOUNT, ACTUAL_SPEND, VARIANCE_AMOUNT, BREACH_STATUS, DETECTED_AT
        ) VALUES (
            SEQ_BREACH_LOG_ID.NEXTVAL, p_category_id, p_month, p_year,
            p_budget_amount, p_actual_spend, p_variance, p_status, CURRENT_TIMESTAMP
        );
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            DBMS_OUTPUT.PUT_LINE('Failed to log breach in autonomous tx: ' || SQLERRM);
    END pr_log_breach;


    -- Procedure Implementation: pr_validate_monthly_budgets
    PROCEDURE pr_validate_monthly_budgets (
        p_month        IN NUMBER,
        p_year         IN NUMBER,
        o_breach_count OUT NUMBER
    ) IS
        v_util_pct  NUMBER(8,2);
        v_variance  NUMBER(12,2);
        v_status    VARCHAR2(20);
        v_net_spend NUMBER(12,2);

        CURSOR cur_budgets IS
            SELECT b.BUDGET_ID, b.CATEGORY_ID, c.CATEGORY_NAME, b.BUDGET_AMOUNT
            FROM MONTHLY_BUDGET b
            JOIN CATEGORIES c ON b.CATEGORY_ID = c.CATEGORY_ID
            WHERE b.BUDGET_MONTH = p_month
              AND b.BUDGET_YEAR = p_year;
    BEGIN
        o_breach_count := 0;
        DBMS_OUTPUT.PUT_LINE('=====================================================================');
        DBMS_OUTPUT.PUT_LINE('STARTING PL/SQL BUDGET AUDIT FOR PERIOD: ' || p_month || '/' || p_year);
        DBMS_OUTPUT.PUT_LINE('=====================================================================');

        FOR rec IN cur_budgets LOOP
            v_status := fn_check_budget_breach(
                p_category_id     => rec.CATEGORY_ID,
                p_month           => p_month,
                p_year            => p_year,
                p_utilization_pct => v_util_pct,
                p_variance_amount => v_variance
            );

            v_net_spend := fn_get_net_spending(rec.CATEGORY_ID, p_month, p_year);

            DBMS_OUTPUT.PUT_LINE(
                'Category: ' || RPAD(rec.CATEGORY_NAME, 16) ||
                ' | Budget: ₹' || TO_CHAR(rec.BUDGET_AMOUNT, '999,990.00') ||
                ' | Net Spend: ₹' || TO_CHAR(v_net_spend, '999,990.00') ||
                ' | Util: ' || LPAD(TO_CHAR(v_util_pct, '990.0'), 5) || '%' ||
                ' | Status: [' || v_status || ']'
            );

            -- Log to breach table if status is BREACH or WARNING
            IF v_status IN ('BREACH', 'WARNING') THEN
                pr_log_breach(
                    p_category_id   => rec.CATEGORY_ID,
                    p_month         => p_month,
                    p_year          => p_year,
                    p_budget_amount => rec.BUDGET_AMOUNT,
                    p_actual_spend  => v_net_spend,
                    p_variance      => v_variance,
                    p_status        => v_status
                );
            END IF;

            IF v_status = 'BREACH' THEN
                o_breach_count := o_breach_count + 1;
            END IF;
        END LOOP;

        DBMS_OUTPUT.PUT_LINE('---------------------------------------------------------------------');
        DBMS_OUTPUT.PUT_LINE('AUDIT FINISHED. Total categories exceeding budget ceiling: ' || o_breach_count);
        DBMS_OUTPUT.PUT_LINE('=====================================================================');

    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('CRITICAL ERROR in pr_validate_monthly_budgets: ' || SQLERRM);
            o_breach_count := -1;
    END pr_validate_monthly_budgets;

END PKG_BUDGET_MANAGEMENT;
/

-- -----------------------------------------------------------------------------
-- DATABASE TRIGGER: TRG_TXN_BUDGET_BREACH_CHECK
-- Evaluates budget impact immediately following new expense entries.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER TRG_TXN_BUDGET_BREACH_CHECK
AFTER INSERT OR UPDATE ON TRANSACTIONS
FOR EACH ROW
WHEN (NEW.TRANSACTION_TYPE = 'EXPENSE')
DECLARE
    v_month      NUMBER;
    v_year       NUMBER;
    v_util_pct   NUMBER(8,2);
    v_variance   NUMBER(12,2);
    v_status     VARCHAR2(20);
    v_budget_amt NUMBER(12,2);
    v_net_spend  NUMBER(12,2);
BEGIN
    v_month := EXTRACT(MONTH FROM :NEW.TRANSACTION_DATE);
    v_year  := EXTRACT(YEAR FROM :NEW.TRANSACTION_DATE);

    v_status := PKG_BUDGET_MANAGEMENT.fn_check_budget_breach(
        p_category_id     => :NEW.CATEGORY_ID,
        p_month           => v_month,
        p_year            => v_year,
        p_utilization_pct => v_util_pct,
        p_variance_amount => v_variance
    );

    IF v_status = 'BREACH' THEN
        SELECT BUDGET_AMOUNT INTO v_budget_amt
        FROM MONTHLY_BUDGET
        WHERE CATEGORY_ID = :NEW.CATEGORY_ID
          AND BUDGET_MONTH = v_month
          AND BUDGET_YEAR = v_year;

        v_net_spend := PKG_BUDGET_MANAGEMENT.fn_get_net_spending(:NEW.CATEGORY_ID, v_month, v_year);

        PKG_BUDGET_MANAGEMENT.pr_log_breach(
            p_category_id   => :NEW.CATEGORY_ID,
            p_month         => v_month,
            p_year          => v_year,
            p_budget_amount => v_budget_amt,
            p_actual_spend  => v_net_spend,
            p_variance      => v_variance,
            p_status        => 'BREACH'
        );
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        NULL; -- Do not abort user transaction if asynchronous logging encounters a delay
END;
/

-- -----------------------------------------------------------------------------
-- ANONYMOUS EXECUTION BLOCK: VERIFY PL/SQL IMPLEMENTATION
-- -----------------------------------------------------------------------------
DECLARE
    v_breaches NUMBER;
BEGIN
    PKG_BUDGET_MANAGEMENT.pr_validate_monthly_budgets(
        p_month        => 10,
        p_year         => 2026,
        o_breach_count => v_breaches
    );
END;
/
