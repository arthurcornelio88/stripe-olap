import pytest
import pandas as pd

def test_csv_shape_vs_invoices(raw_json_dump, olap_outputs):
    """Row count of fact_invoices.csv should match number of invoices in dump."""
    expected_len = len(raw_json_dump["invoices"])
    actual_len = len(olap_outputs["fact_invoices"])
    assert actual_len == expected_len, f"CSV has {actual_len} rows but expected {expected_len}"

def test_required_columns(olap_outputs):
    """Check required columns are present in the CSV."""
    df = olap_outputs["fact_invoices"]
    expected_columns = [
        "invoice_id", "customer_id", "customer_email", "amount_paid", "currency", "status", "created_at",
        "period_start", "period_end", "product_id", "product_name", "price_id", "plan_amount", "plan_interval",
        "subscription_id", "payment_method_type", "receipt_number", "livemode", "card_brand"
    ]
    missing = set(expected_columns) - set(df.columns)
    assert not missing, f"Missing columns in CSV: {missing}"

def test_column_types(olap_outputs):
    """Ensure some important columns have correct types."""
    df = olap_outputs["fact_invoices"]
    assert pd.api.types.is_integer_dtype(df["amount_paid"])
    assert pd.api.types.is_string_dtype(df["invoice_id"])
    assert pd.api.types.is_bool_dtype(df["livemode"]) or df["livemode"].isnull().all()
