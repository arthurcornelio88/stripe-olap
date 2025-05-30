CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    DATE_TRUNC('month', created_at) AS month,
    SUM(amount_paid) AS total_revenue
FROM fact_invoices
GROUP BY 1
ORDER BY 1;


CREATE OR REPLACE VIEW vw_active_subscriptions AS
SELECT *
FROM dim_subscriptions
WHERE status = 'active';


CREATE OR REPLACE VIEW vw_customer_ltv AS
SELECT
    customer_id,
    SUM(amount_paid) AS lifetime_value
FROM fact_invoices
GROUP BY customer_id;

