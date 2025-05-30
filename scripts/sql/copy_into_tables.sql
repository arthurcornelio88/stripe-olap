COPY INTO fact_invoices (
    invoice_id,
    customer_id,
    customer_email,
    amount_paid,
    currency,
    status,
    created_at,
    period_start,
    period_end,
    product_id,
    product_name,
    price_id,
    plan_amount,
    plan_interval,
    subscription_id,
    payment_method_type,
    receipt_number,
    livemode,
    card_brand
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/fact_invoices.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_customers (
    customer_id,
    email,
    name,
    delinquent,
    currency,
    livemode,
    created_at
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_customers.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_products (
    product_id,
    name,
    description,
    active,
    created_at,
    updated_at
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_products.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_prices (
    price_id,
    product_id,
    currency,
    unit_amount,
    type,
    billing_scheme,
    recurring_interval,
    recurring_count,
    recurring_usage_type,
    livemode,
    created_at
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_prices.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_payment_methods (
    payment_method_id,
    type,
    customer_id,
    livemode,
    created_at,
    card_brand
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_payment_methods.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_subscriptions (
    subscription_id,
    customer_id,
    price_id,
    status,
    currency,
    start_date,
    created_at,
    cancel_at,
    ended_at,
    plan_interval,
    livemode
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_subscriptions.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_payment_intents (
    payment_intent_id,
    customer_id,
    invoice_id,
    status,
    amount,
    currency,
    created_at
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_payment_intents.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);
COPY INTO dim_charges (
    charge_id,
    payment_intent_id,
    customer_id,
    amount,
    currency,
    status,
    paid,
    created_at
)
FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/dim_charges.csv
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_DELIMITER = ',',
    SKIP_HEADER = 1
);