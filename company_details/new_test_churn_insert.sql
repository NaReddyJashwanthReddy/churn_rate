/* ================================================================
   Test Data for Churn Prediction Model
   
   This script creates a test table and populates it with diverse
   customer profiles to test the churn prediction model.
   
   NOTE: Churn_flag is NOT included as we are testing predictions
   ================================================================ */

-- Step 1: Create a view without churn_flag for testing
CREATE OR REPLACE VIEW churn_test_data_view AS
SELECT 
    customer_id,
    plan_type,
    tenure_days,
    watch_hours_30d,
    login_count_30d,
    days_since_last_login,
    support_ticket_count,
    payment_failure_count,
    monthly_revenue
FROM churn_analytics_data;

-- Step 2: Create test table (dropping if exists to allow re-runs)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE churn_test_predictions';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
/

CREATE TABLE churn_test_predictions (
    customer_id            NUMBER(10)      NOT NULL,
    plan_type              VARCHAR2(20)    NOT NULL,
    tenure_days            NUMBER(5)       NOT NULL,
    watch_hours_30d        NUMBER(8,2)     NOT NULL,
    login_count_30d        NUMBER(5)       NOT NULL,
    days_since_last_login  NUMBER(5)       NOT NULL,
    support_ticket_count   NUMBER(5)       DEFAULT 0,
    payment_failure_count  NUMBER(5)       DEFAULT 0,
    monthly_revenue        NUMBER(8,2)     NOT NULL
);

ALTER TABLE churn_test_predictions
    ADD CONSTRAINT churn_test_pk
        PRIMARY KEY (customer_id);

-- Step 3: Populate test data with diverse customer profiles
-- These test cases cover different churn risk scenarios

INSERT INTO churn_test_predictions VALUES
-- ========== HIGH CHURN RISK PROFILES ==========
-- New customer with low engagement and support issues
(101001, 'Basic', 15, 5.5, 2, 25, 5, 2, 9.99),
(101002, 'Basic', 20, 2.0, 1, 30, 4, 1, 9.99),
(101003, 'Premium', 45, 8.0, 3, 28, 6, 3, 14.99),
(101004, 'Basic', 30, 3.5, 2, 22, 7, 2, 9.99),
(101005, 'Family', 60, 10.0, 4, 35, 5, 4, 29.99),

-- ========== MEDIUM CHURN RISK PROFILES ==========
-- Moderate tenure with mixed engagement
(102001, 'Basic', 90, 20.0, 8, 10, 2, 1, 9.99),
(102002, 'Premium', 120, 35.0, 12, 5, 3, 1, 14.99),
(102003, 'Basic', 75, 15.0, 5, 15, 4, 0, 9.99),
(102004, 'Family', 100, 45.0, 10, 8, 2, 1, 29.99),
(102005, 'Premium', 150, 40.0, 14, 3, 1, 0, 14.99),

-- ========== LOW CHURN RISK PROFILES ==========
-- Long-term customers with high engagement
(103001, 'Premium', 365, 95.0, 28, 1, 0, 0, 14.99),
(103002, 'Family', 400, 150.0, 30, 0, 0, 0, 29.99),
(103003, 'Premium', 500, 110.0, 25, 1, 1, 0, 14.99),
(103004, 'Family', 600, 180.0, 28, 2, 0, 0, 29.99),
(103005, 'Premium', 700, 130.0, 26, 1, 0, 0, 14.99),

-- ========== EDGE CASES & BOUNDARY CONDITIONS ==========
-- New customers (first 7 days)
(104001, 'Basic', 5, 0.5, 1, 5, 0, 0, 9.99),
(104002, 'Premium', 7, 2.0, 1, 7, 1, 0, 14.99),

-- Inactive for extended period
(104003, 'Basic', 180, 5.0, 0, 90, 1, 0, 9.99),
(104004, 'Premium', 250, 10.0, 2, 60, 2, 1, 14.99),

-- Multiple payment failures
(104005, 'Family', 120, 50.0, 15, 3, 0, 5, 29.99),

-- Zero activity indicators
(104006, 'Basic', 90, 0.0, 0, 365, 0, 0, 9.99),
(104007, 'Premium', 200, 5.0, 1, 200, 8, 0, 14.99),

-- ========== BALANCED TEST CASES ==========
-- Mixed scenarios for comprehensive testing
(105001, 'Basic', 180, 60.0, 20, 2, 0, 0, 9.99),
(105002, 'Premium', 240, 75.0, 18, 3, 1, 0, 14.99),
(105003, 'Family', 180, 90.0, 16, 4, 0, 0, 29.99),
(105004, 'Basic', 100, 25.0, 10, 5, 2, 1, 9.99),
(105005, 'Premium', 300, 85.0, 20, 2, 0, 0, 14.99),

-- ========== STRESS TEST CASES ==========
-- Maximum and minimum values
(106001, 'Family', 1000, 500.0, 31, 0, 0, 0, 29.99),
(106002, 'Basic', 1, 0.0, 0, 1, 0, 0, 9.99),
(106003, 'Premium', 365, 0.1, 1, 365, 10, 10, 14.99);

COMMIT;

-- Step 4: Verification and Summary
SELECT 'Test data population completed successfully!' AS status FROM dual;

-- Display test data statistics
SELECT 
    COUNT(*) as total_records,
    ROUND(AVG(tenure_days), 2) as avg_tenure,
    ROUND(AVG(watch_hours_30d), 2) as avg_watch_hours,
    ROUND(AVG(login_count_30d), 2) as avg_login_count,
    ROUND(AVG(support_ticket_count), 2) as avg_support_tickets,
    ROUND(AVG(payment_failure_count), 2) as avg_payment_failures
FROM churn_test_predictions;

-- Display all test records
SELECT * FROM churn_test_predictions ORDER BY customer_id;

COMMIT;