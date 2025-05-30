import json
import pandas as pd

def parse_json_column(col, key):
    def extract(val):
        try:
            if pd.isnull(val):
                return None
            return json.loads(val).get(key)
        except Exception:
            return None
    return extract

def flatten_dim_prices(df: pd.DataFrame) -> pd.DataFrame:
    df["recurring_interval"] = df["recurring"].apply(parse_json_column("recurring", "interval"))
    df["recurring_count"] = df["recurring"].apply(parse_json_column("recurring", "interval_count"))
    df["recurring_usage_type"] = df["recurring"].apply(parse_json_column("recurring", "usage_type"))
    return df.drop(columns=["recurring"])

# Mapping rules (can be extended)
FLATTEN_RULES = {
    "dim_prices": flatten_dim_prices,
    # future: "fact_invoices": flatten_fact_invoices
}

def apply_flatten_if_needed(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    flatten_fn = FLATTEN_RULES.get(table_name)
    if flatten_fn:
        return flatten_fn(df)
    return df
