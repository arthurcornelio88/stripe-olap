CREATE OR REPLACE TABLE fact_invoices (
    invoice_id STRING,
    customer_id STRING,
    customer_email STRING,
    amount_paid NUMBER,
    currency STRING,
    status STRING,
    created_at TIMESTAMP,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    product_id STRING,
    product_name STRING,
    price_id STRING,
    plan_amount NUMBER,
    plan_interval STRING,
    subscription_id STRING,
    payment_method_type STRING,
    receipt_number STRING,
    livemode BOOLEAN,
    card_brand STRING
);

CREATE OR REPLACE TABLE dim_customers (
    customer_id STRING,
    email STRING,
    name STRING,
    delinquent BOOLEAN,
    currency STRING,
    livemode BOOLEAN,
    created_at TIMESTAMP
);

CREATE OR REPLACE TABLE dim_products (
    product_id STRING,
    name STRING,
    description STRING,
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE OR REPLACE TABLE dim_prices (
    price_id STRING,
    product_id STRING,
    currency STRING,
    unit_amount NUMBER,
    type STRING,
    billing_scheme STRING,
    recurring_interval STRING,
    recurring_count NUMBER,
    recurring_usage_type STRING,
    livemode BOOLEAN,
    created_at TIMESTAMP
);

CREATE OR REPLACE TABLE dim_payment_methods (
    payment_method_id STRING,
    type STRING,
    customer_id STRING,
    livemode BOOLEAN,
    created_at TIMESTAMP,
    card_brand STRING
);

CREATE OR REPLACE TABLE dim_subscriptions (
    subscription_id STRING,
    customer_id STRING,
    price_id STRING,
    status STRING,
    currency STRING,
    start_date TIMESTAMP,
    created_at TIMESTAMP,
    cancel_at TIMESTAMP,
    ended_at TIMESTAMP,
    plan_interval STRING,
    livemode BOOLEAN
);

CREATE OR REPLACE TABLE dim_payment_intents (
    payment_intent_id STRING,
    customer_id STRING,
    invoice_id STRING,
    status STRING,
    amount NUMBER,
    currency STRING,
    created_at TIMESTAMP
);

CREATE OR REPLACE TABLE dim_charges (
    charge_id STRING,
    payment_intent_id STRING,
    customer_id STRING,
    amount NUMBER,
    currency STRING,
    status STRING,
    paid BOOLEAN,
    created_at TIMESTAMP
);
