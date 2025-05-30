import pandas as pd

# This module contains functions to build fact invoices and dimension tables from a JSON dump of Stripe data.

### Fact Table Builder
def build_fact_invoices(data):
    invoices = pd.DataFrame(data["invoices"])
    customers = pd.DataFrame(data["customers"])
    subscriptions = pd.DataFrame(data["subscriptions"])
    products = pd.DataFrame(data["products"])
    prices = pd.DataFrame(data["prices"])
    payment_methods = pd.DataFrame(data["payment_methods"])

    invoices["invoice_id"] = invoices["id"]
    invoices["subscription_id"] = invoices["lines"].apply(
        lambda x: x["data"][0]["parent"]["subscription_item_details"]["subscription"]
    )
    invoices["price_id"] = invoices["lines"].apply(
        lambda x: x["data"][0]["pricing"]["price_details"]["price"]
    )
    invoices["product_id"] = invoices["lines"].apply(
        lambda x: x["data"][0]["pricing"]["price_details"]["product"]
    )

    df = invoices.merge(customers[["id", "email"]], left_on="customer_id", right_on="id", suffixes=("", "_customer"))
    df = df.merge(subscriptions[["id", "price_id", "plan_interval"]], left_on="subscription_id", right_on="id", suffixes=("", "_sub"))
    df = df.merge(products[["id", "name"]], left_on="product_id", right_on="id", suffixes=("", "_product"))
    df = df.merge(prices[["id", "unit_amount"]], left_on="price_id", right_on="id", suffixes=("", "_price"))
    df = df.merge(payment_methods[["id", "type", "card"]], how="left", left_on="default_payment_method_id", right_on="id")

    df_final = df[[
        "invoice_id", "customer_id", "email", "amount_paid", "currency", "status", "created", "period_start",
        "period_end", "product_id", "name", "price_id", "unit_amount", "plan_interval",
        "subscription_id", "type", "card", "receipt_number", "livemode"
    ]].rename(columns={
        "email": "customer_email",
        "created": "created_at",
        "name": "product_name",
        "unit_amount": "plan_amount",
        "type": "payment_method_type",
        "card": "card_info"
    })

    df_final["card_brand"] = df_final["card_info"].apply(lambda x: x.get("brand") if isinstance(x, dict) else None)
    df_final.drop(columns=["card_info"], inplace=True)

    return df_final

### Dimension Table Builders
def build_dim_subscriptions(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data["subscriptions"])
    
    # Flatten first item for now
    def extract_price_id(sub):
        try:
            return sub["items"]["data"][0]["price"]["id"]
        except:
            return None

    df["price_id"] = df.apply(extract_price_id, axis=1)

    return df[[
        "id", "customer_id", "price_id", "status", "currency", "start_date",
        "created", "cancel_at", "ended_at", "plan_interval", "livemode"
    ]].rename(columns={
        "id": "subscription_id",
        "created": "created_at"
    })

def build_dim_payment_methods(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data["payment_methods"])
    df["card_brand"] = df["card"].apply(lambda x: x.get("brand") if isinstance(x, dict) else None)
    return df[[
        "id", "type", "customer_id", "livemode", "created", "card_brand"
    ]].rename(columns={
        "id": "payment_method_id",
        "created": "created_at"
    })

def build_dim_prices(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data["prices"])
    return df[[
        "id", "product_id", "currency", "unit_amount", "type",
        "billing_scheme", "recurring", "livemode", "created"
    ]].rename(columns={
        "id": "price_id",
        "created": "created_at"
    })

def build_dim_products(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data["products"])
    return df[["id", "name", "description", "active", "created", "updated"]].rename(columns={
        "id": "product_id",
        "created": "created_at",
        "updated": "updated_at"
    })

def build_dim_customers(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data["customers"])
    return df[["id", "email", "name", "delinquent", "currency", "livemode", "created"]].rename(columns={
        "id": "customer_id",
        "created": "created_at"
    })

def build_dim_payment_intents(raw: dict) -> pd.DataFrame:
    df = pd.DataFrame(raw.get("payment_intents", []))
    if df.empty:
        return pd.DataFrame(columns=[
            "payment_intent_id", "customer_id", "invoice_id",
            "status", "amount", "currency", "created_at"
        ])
    return pd.DataFrame({
        "payment_intent_id": df["id"],
        "customer_id": df.get("customer_id", pd.NA),
        "invoice_id": df.get("invoice", pd.NA),
        "status": df["status"],
        "amount": df["amount"],
        "currency": df["currency"],
        "created_at": pd.to_datetime(df["created"])
    })

def build_dim_charges(raw: dict) -> pd.DataFrame:
    df = pd.DataFrame(raw.get("charges", []))
    if df.empty:
        return pd.DataFrame(columns=[
            "charge_id", "payment_intent_id", "customer_id",
            "amount", "currency", "status", "paid", "created_at"
        ])
    return pd.DataFrame({
        "charge_id": df["id"],
        "payment_intent_id": df.get("payment_intent", pd.NA),
        "customer_id": df.get("customer_id", pd.NA),
        "amount": df["amount"],
        "currency": df["currency"],
        "status": df["status"],
        "paid": df["paid"],
        "created_at": pd.to_datetime(df["created"])
    })
