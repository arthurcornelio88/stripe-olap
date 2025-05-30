# 📊 Fact Table Design: `fact_invoices`

This document outlines the design and construction logic behind the `fact_invoices` table in our OLAP schema, which is derived from the normalized Stripe data originally stored in a JSON OLTP format.

---

## 🔍 Purpose

The `fact_invoices` table serves as the **central fact table** in our data warehouse. Each row represents **a single invoice** issued to a customer, enriched with related contextual data.

This table enables analytical queries such as:
- Revenue by product, customer, plan, or period
- Invoice volume trends
- Conversion or churn rates
- Aggregates across plans or cohorts

---

## 🏗️ Source Tables

The table is built by merging and transforming data from:

| Source Table        | Usage                                                             |
|---------------------|--------------------------------------------------------------------|
| `invoices`          | Base of the fact table (one row = one invoice)                    |
| `customers`         | Enriches customer details (email, country, delinquent, etc.)      |
| `subscriptions`     | Plan and billing metadata (linked via `subscription_id`)          |
| `products`          | Name, description of the purchased product                        |
| `prices`            | Price amount, currency, interval, billing scheme, etc.            |
| `payment_methods`   | Type of payment (card, etc.), funding source, etc.                |

---

## 🧱 Table Schema

| Column Name              | Type        | Description                                                 |
|--------------------------|-------------|-------------------------------------------------------------|
| `invoice_id`             | TEXT        | Unique Stripe invoice ID                                    |
| `customer_id`            | TEXT        | FK to customer                                              |
| `customer_email`         | TEXT        | Email of the customer                                       |
| `amount_paid`            | INTEGER     | Final amount paid (in cents)                                |
| `currency`               | TEXT        | Currency code (e.g. eur, usd)                               |
| `status`                 | TEXT        | Payment status (paid, draft, uncollectible, etc.)           |
| `created_at`             | TIMESTAMP   | Invoice creation timestamp                                  |
| `period_start`           | TIMESTAMP   | Start of billed period                                      |
| `period_end`             | TIMESTAMP   | End of billed period                                        |
| `product_id`             | TEXT        | Stripe product ID                                           |
| `product_name`           | TEXT        | Human-friendly product label                                |
| `price_id`               | TEXT        | Stripe price object ID                                      |
| `plan_amount`            | INTEGER     | Recurring amount for the plan                               |
| `plan_interval`          | TEXT        | Billing interval (month, year, etc.)                        |
| `subscription_id`        | TEXT        | FK to `subscriptions`                                       |
| `payment_method_type`    | TEXT        | Method used (e.g. card, bank_transfer)                      |
| `card_brand`             | TEXT        | Brand of the card (visa, mastercard, etc.)                  |
| `receipt_url`            | TEXT        | Public link to the invoice receipt                          |
| `livemode`               | BOOLEAN     | Stripe environment (true = live, false = test)              |

---

## 🧠 Design Considerations

* ✅ All joins are **1-to-1 or 1-to-N**, ensuring referential integrity.
* ✅ We normalize nested fields (e.g. invoice lines, subscription items) to get granular data.
* ✅ Enriched dimensions allow grouping, filtering and slicing metrics by multiple axes.

---

### ✅ Why `payment_intents` and `charges` Are Now Included Separately

While `payment_intents` and `charges` are crucial to understanding the Stripe payment lifecycle (`invoice → payment_intent → charge`), they are intentionally **not embedded inside `fact_invoices`**, but instead exposed via their own dimension tables:

- `dim_payment_intents`
- `dim_charges`

This design reflects the following principles:

* 🔄 **Asynchronous Events**  
  Payment objects evolve independently — some invoices are finalized before any payment intent is confirmed or captured.

* 📄 **Separation of Concerns**  
  `fact_invoices` focuses on **invoice-level** logic (billing intent), while payment events (auth, success, failure) are treated in **dedicated tables** to avoid mixing layers.

* 🔍 **Joinability When Needed**  
  Fields like `status`, `receipt_email`, or fraud metadata from charges can be joined externally using `payment_intent_id`, allowing fraud/risk pipelines or reconciliation logic to plug in easily.

This modular structure keeps `fact_invoices` clean and auditable, while providing all raw material needed for deeper payment insights.

---

## 📁 Location

Data source file:  
```plaintext
gs://stripe-oltp-bucket-prod/dump/db_dump_prod_YYYY-MM-DD.json
```

Latest run: `2025-05-30 10:51:29`

---
