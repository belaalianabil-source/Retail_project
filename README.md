# retail_q: Retail Data Pipeline

A Databricks **Lakeflow Declarative Pipelines** project (PySpark) that ingests retail data from multiple sources and transforms it through a **medallion architecture**: Bronze → Silver → Gold.

## Overview

The pipeline combines CRM data from Salesforce, operational data from PostgreSQL, and transaction files from cloud blob storage into clean, validated Silver tables. These feed a Gold-layer sales fact table ready for analytics and reporting.

## Architecture

```
 Sources                 Bronze                      Silver                          Gold
 ───────                 ──────                      ──────                          ────
 Salesforce      ──►  salesforse_bronze     ──►  bronze_to_silver.account
                                                 bronze_to_silver.opportunity ──┐
 PostgreSQL      ──►  postgesql_nronze      ──►  bronze_to_silver.inventory     │
                                                 bronze_to_silver.product_catalog│
 Blob storage    ──►  blob_bronze           ──►  bronze_to_silver.transactions ─┴─►  silver_to_gold.fact_sales
```

All tables live in the Unity Catalog catalog `retail_q`.

## Project Structure

```
.
├── account.py          # Silver: Salesforce accounts
├── opportunity.py      # Silver: Salesforce opportunities
├── inventory.py        # Silver: store inventory (PostgreSQL)
├── product_catalog.py  # Silver: product master data (PostgreSQL)
├── transactions.py     # Silver: sales transactions (blob storage)
└── fact_sales.py       # Gold: sales fact table
```

## Tables

### Silver layer (`retail_q.bronze_to_silver`)

| Table | Source | Type | What it does |
|---|---|---|---|
| `account` | `salesforse_bronze.account` | Streaming | Selects core business columns, renames them to snake_case, uppercases and trims customer names, defaults missing industry to `UNKNOWN`, and derives `is_active` from `__END_AT`. |
| `opportunity` | `salesforse_bronze.opportunity` | Streaming | Selects core sales columns and derives `deal_size` (`ENTERPRISE` > 100,000, `MID_MARKET` > 25,000, otherwise `SMALL`). |
| `inventory` | `postgesql_nronze.inventory` | Streaming | Derives `inventory_status` (`LOW_STOCK` when stock is below the reorder level, otherwise `HEALTHY`) and adds a `processed_at` timestamp. |
| `product_catalog` | `postgesql_nronze.product_catalog` | Streaming | Standardizes text fields, rounds prices, fills missing subcategory and brand, and derives a price segment (`PREMIUM`, `MEDIUM`, `ECONOMY`, `CHEAP`). Keeps SCD history via `start_at` and `end_at`. |
| `transactions` | `blob_bronze.transactions` | Batch | Casts numeric columns, computes `gross_amount` (quantity × selling price), and parses the timestamp from `dd-MMM-yyyy hh.mm.ss a` format. |

### Gold layer (`retail_q.silver_to_gold`)

| Table | Description |
|---|---|
| `fact_sales` | Left joins `transactions` to `opportunity` on a normalized (upper-cased, trimmed) opportunity name. Adds `transaction_date`, opportunity stage, owner, amount, and `customer_id` (the opportunity's account ID). |

## Data Quality

Data quality rules are enforced with pipeline expectations. `expect_or_drop` removes failing rows; `expect` records violations but keeps the rows.

| Table | Drop rows when | Warn when |
|---|---|---|
| `account` | `id` is null | `customer_name` is null |
| `opportunity` | `id` is null | `name` is null; `amount` < 0; `probability` outside 0–100; `stage_name` not in (`Prospecting`, `Closed Won`, `Closed Lost`) |
| `inventory` | `product_id` is null or blank | `inventory_id` or `store_id` is null |
| `product_catalog` | `product_id`, `product_name` or `supplier_name` is null or blank | `category` is null; `unit_price` ≤ 0 |
| `transactions` | `transaction_id` is null | `quantity` ≤ 0; negative `selling_price` or `discount_amount`; null `product_id`; `payment_mode` not in (`UPI`, `Card`, `Cash`, `Net Banking`) |

## Prerequisites

- A Databricks workspace with **Unity Catalog** enabled
- Permission to create pipelines and write to the `retail_q` catalog
- Bronze tables already ingested into these schemas:
  - `retail_q.salesforse_bronze` (`account`, `opportunity`)
  - `retail_q.postgesql_nronze` (`inventory`, `product_catalog`)
  - `retail_q.blob_bronze` (`transactions`)
- Target schemas `bronze_to_silver` and `silver_to_gold` in the `retail_q` catalog

## Getting Started

1. **Clone the repository** into your Databricks workspace, for example with Git folders:
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   ```
2. **Create a pipeline** in Databricks (Jobs & Pipelines → Create → ETL pipeline).
3. **Add the source files** (`account.py`, `opportunity.py`, `inventory.py`, `product_catalog.py`, `transactions.py`, `fact_sales.py`) to the pipeline.
4. **Set the target catalog** to `retail_q`.
5. **Run** the pipeline. Databricks resolves the dependencies between tables automatically.
6. **Monitor** data quality metrics in the pipeline's event log and UI.

## Tech Stack

- Databricks Lakeflow Declarative Pipelines (`pyspark.pipelines`)
- PySpark
- Unity Catalog
- Salesforce, PostgreSQL and cloud blob storage as sources

## Contributing

Contributions are welcome. Please open an issue to discuss a change before submitting a pull request.

## License

Add your license here (for example, MIT).
