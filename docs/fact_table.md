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

### ❓ Why `payment_intents` and `charges` Are Not Included (Yet)

While `payment_intents` and `charges` contain critical payment lifecycle data (authorization, capture, and payment outcomes), they are **not directly embedded** in this version of the `fact_invoices` table for the following reasons:

* 🔄 **Decoupling of Payment Events**: Stripe’s `invoice → payment_intent → charge` chain is *asynchronous*. Not every invoice has a 1-to-1 relationship with a final charge — making it complex to ensure accurate joins without risking duplicate or partial data.

* 📄 **Separation of Concerns**: The current goal of `fact_invoices` is to serve **billing-level analytics**, centered around issued and finalized invoices. Including payment event granularity would mix behavioral and financial layers.

* 🔍 **Optional Enrichment**: Payment intent metadata (e.g., `receipt_email`, `payment_method_details`) can be joined externally when needed for deeper fraud/risk analysis — or used to build a future `fact_payments` table.

A future iteration may include these fields once we finalize a clear, idempotent mapping logic. Until then, this separation keeps the invoice logic lean and auditable.

---

## 📁 Location

Data source file:  
```plaintext
gs://stripe-oltp-bucket-prod/dump/db_dump_prod_YYYY-MM-DD.json
```

Latest run: `2025-05-30 10:51:29`

---
