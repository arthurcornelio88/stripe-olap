Here is the fully **refactored English version** of your `fact_dim.md` file, updated with `<img src="/docs/img/..."/>` references and preserving the full structure and intent of your original document.

---

# 📊 Fact Table Design: `fact_invoices`

This document describes the design and construction logic of the `fact_invoices` table in our OLAP schema, built from raw Stripe JSON data extracted from the OLTP layer.

---

## 🔍 Purpose

The `fact_invoices` table is the **central analytical table** in our data warehouse. Each row represents **a single invoice**, enriched with contextual information from related tables like customers, products, subscriptions, etc.

This table enables analytical use cases such as:

* Revenue by product, customer, or time period
* Invoice volume trends
* Conversion and churn rates
* Aggregations across pricing plans or cohorts

---

## 🏗️ Source Tables

| Source Table      | Usage Description                                     |
| ----------------- | ----------------------------------------------------- |
| `invoices`        | Base for the fact table (1 row = 1 invoice)           |
| `customers`       | Adds customer-level details (email, currency, status) |
| `subscriptions`   | Adds plan metadata like interval, duration            |
| `products`        | Adds product name and metadata                        |
| `prices`          | Enriches with amount, currency, billing details       |
| `payment_methods` | Provides payment type, card brand, etc.               |

---

## 🧱 `fact_invoices` Table Schema

| Column Name           | Type      | Description                                    |
| --------------------- | --------- | ---------------------------------------------- |
| `invoice_id`          | TEXT      | Unique Stripe invoice ID                       |
| `customer_id`         | TEXT      | Foreign key to the customer                    |
| `customer_email`      | TEXT      | Email address of the customer                  |
| `amount_paid`         | INTEGER   | Amount paid in cents                           |
| `currency`            | TEXT      | Currency code (e.g., eur, usd)                 |
| `status`              | TEXT      | Payment status (paid, draft, etc.)             |
| `created_at`          | TIMESTAMP | Invoice creation date                          |
| `period_start`        | TIMESTAMP | Billing period start                           |
| `period_end`          | TIMESTAMP | Billing period end                             |
| `product_id`          | TEXT      | Associated Stripe product ID                   |
| `product_name`        | TEXT      | Human-readable product label                   |
| `price_id`            | TEXT      | Stripe price object ID                         |
| `plan_amount`         | INTEGER   | Amount associated with the plan                |
| `plan_interval`       | TEXT      | Billing interval (e.g., month, year)           |
| `subscription_id`     | TEXT      | Foreign key to the subscription                |
| `payment_method_type` | TEXT      | Payment method (e.g., card, bank\_transfer)    |
| `card_brand`          | TEXT      | Card brand (e.g., Visa, Mastercard)            |
| `receipt_number`      | TEXT      | Stripe receipt reference                       |
| `livemode`            | BOOLEAN   | Stripe environment (true = live, false = test) |

---

## 🏗️ Dimension Tables (`dim_*`)

Each dimension table is built independently with its own transformation logic. These dimensions enrich `fact_invoices` and can be used for analytical joins.

### Generated Dimensions Overview:

| Table                 | Primary Key         | Description                                         |
| --------------------- | ------------------- | --------------------------------------------------- |
| `dim_customers`       | `customer_id`       | Email, currency, status, creation date, live mode   |
| `dim_products`        | `product_id`        | Product name, description, active flag, timestamps  |
| `dim_prices`          | `price_id`          | Currency, amount, type, billing interval, etc.      |
| `dim_payment_methods` | `payment_method_id` | Type, card brand, associated customer               |
| `dim_subscriptions`   | `subscription_id`   | Status, key dates, price, currency, plan interval   |
| `dim_payment_intents` | `payment_intent_id` | Amount, status, customer, currency                  |
| `dim_charges`         | `charge_id`         | Amount, status, linked payment intent, created date |

Each dimension is extracted, flattened, and saved independently as a CSV file to a Google Cloud Storage bucket.

---

## 🧠 Design Considerations

* ✅ All joins are **1-to-1 or 1-to-N**, ensuring referential integrity
* ✅ Nested fields (like invoice lines) are normalized for granular reporting
* ✅ Enriched dimension joins support flexible filtering and aggregation

---

### ✅ Why `payment_intents` and `charges` Are Included Separately

Although `payment_intents` and `charges` are central to understanding Stripe’s payment lifecycle (`invoice → payment_intent → charge`), they are **not embedded** inside `fact_invoices`. Instead, they are represented in their **own dimension tables**:

* `dim_payment_intents`
* `dim_charges`

This follows key principles:

* 🔄 **Asynchronous Events**
  Payment objects evolve on separate timelines — invoices can be finalized before any payment is captured.

* 📄 **Separation of Concerns**
  `fact_invoices` focuses on **billing intent**, while payments (success/failure) live in **dedicated layers**.

* 🔍 **Joinability When Needed**
  Events like fraud detection or payment reconciliation can join via `payment_intent_id`.

This modular structure ensures that `fact_invoices` stays clean, while still offering deep insights when needed.

---

## ✅ Data Validation via Pytest

An automated Pytest suite validates the CSV exports against the raw OLTP JSON dump. This is fully **integrated into the `make all` process**, ensuring integrity before loading.

### ✔️ For `fact_invoices`

* **Shape & Volume**

  * `test_csv_shape_vs_invoices`: ensures each invoice in JSON matches a row in the CSV
* **Required Columns**

  * `test_required_columns`: validates schema conformity
* **Type Checks**

  * `test_column_types`: ensures `amount_paid` is integer, `livemode` is boolean

### ✔️ For All `dim_*` Tables

* `test_required_columns_dim_tables`: all mandatory fields are present
* `test_no_duplicate_ids`: no duplicates in the primary ID column
* `test_not_empty`: table must contain at least one row

### 📸 Pytest Output Example

<img src="docs/img/etl2.png" alt="etl2"  width="500"/>

---

## 📁 Data Location

All CSV outputs are saved to GCS (shared bucket):

```
gs://stripe-bucket-prod_v3/olap_outputs/{timestamp}/
```

Example from May 31, 2025:

<img src="/docs/img/etl11.png" width="750"/>

---

## 🚀 One-Command Orchestration

The full ETL process — including extraction, transformation, saving, and validation — is launched with:

```bash
make all ENV=PROD
```

<img src="/docs/img/etl1.png" width="750"/>

---

Let me know if you'd like to proceed with a similar breakdown for each `dim_*` table.
