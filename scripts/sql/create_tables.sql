create or replace table fact_invoices (
    invoice_id string,
    customer_email string,
    amount number,
    currency string,
    status string,
    created_at timestamp
);

create or replace table dim_customers (
    customer_id string,
    email string,
    created_at timestamp
);

create or replace table dim_products (
    product_id string,
    name string,
    description string
);

create or replace table dim_prices (
    price_id string,
    product_id string,
    unit_amount number,
    currency string,
    recurring_interval string
);

create or replace table dim_payment_methods (
    payment_method_id string,
    type string,
    customer_id string
);

create or replace table dim_subscriptions (
    subscription_id string,
    customer_id string,
    status string,
    start_date timestamp,
    end_date timestamp
);

create or replace table dim_payment_intents (
    payment_intent_id string,
    amount number,
    currency string,
    status string,
    created_at timestamp
);

create or replace table dim_charges (
    charge_id string,
    amount number,
    currency string,
    status string,
    created_at timestamp
);
