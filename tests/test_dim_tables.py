import pytest
import pandas as pd

DIM_EXPECTATIONS = {
    "dim_customers": {
        "required_columns": ["customer_id", "email", "name", "delinquent", "currency", "livemode", "created_at"],
        "id_column": "customer_id"
    },
    "dim_products": {
        "required_columns": ["product_id", "name", "description", "active", "created_at", "updated_at"],
        "id_column": "product_id"
    },
    "dim_prices": {
        "required_columns": ["price_id", "product_id", "currency", "unit_amount", "type", "billing_scheme", "recurring", "livemode", "created_at"],
        "id_column": "price_id"
    },
    "dim_payment_methods": {
        "required_columns": ["payment_method_id", "type", "customer_id", "livemode", "created_at", "card_brand"],
        "id_column": "payment_method_id"
    },
    "dim_subscriptions": {
        "required_columns": ["subscription_id", "customer_id", "price_id", "status", "currency", "start_date", "created_at", "cancel_at", "ended_at", "plan_interval", "livemode"],
        "id_column": "subscription_id"
    },
}

@pytest.mark.parametrize("table_name", DIM_EXPECTATIONS.keys())
def test_required_columns_dim_tables(olap_outputs, table_name):
    df = olap_outputs[table_name]
    expected_cols = DIM_EXPECTATIONS[table_name]["required_columns"]
    missing = set(expected_cols) - set(df.columns)
    assert not missing, f"{table_name} missing columns: {missing}"

@pytest.mark.parametrize("table_name", DIM_EXPECTATIONS.keys())
def test_no_duplicate_ids(olap_outputs, table_name):
    df = olap_outputs[table_name]
    id_col = DIM_EXPECTATIONS[table_name]["id_column"]
    duplicates = df[id_col].duplicated().sum()
    assert duplicates == 0, f"{table_name} has {duplicates} duplicate {id_col} values"

@pytest.mark.parametrize("table_name", DIM_EXPECTATIONS.keys())
def test_not_empty(olap_outputs, table_name):
    df = olap_outputs[table_name]
    assert len(df) > 0, f"{table_name} is empty!"
