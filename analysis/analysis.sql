/* the total number of records*/
SELECT 
    COUNT(*)
FROM churn_analytics_data;

/* the number of customers who have churned vs those who have not */
SELECT churn_flag,
       COUNT(*) AS customers
FROM churn_analytics_data
GROUP BY churn_flag;

/*Which plans are most common?*/
SELECT plan_type,
       COUNT(*)
FROM churn_analytics_data
GROUP BY plan_type;

/*What is the average monthly revenue by plan type?*/
SELECT plan_type,
       AVG(monthly_revenue)
FROM churn_analytics_data
GROUP BY plan_type;