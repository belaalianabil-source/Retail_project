# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC CREATE OR REPLACE TABLE retail_q.silver_to_gold.dim_calendar AS
# MAGIC
# MAGIC WITH date_range AS (
# MAGIC
# MAGIC     SELECT explode(
# MAGIC         sequence(
# MAGIC             DATE '2025-01-01',
# MAGIC              DATE '2028-12-31',
# MAGIC             interval 1 day
# MAGIC         )
# MAGIC     ) AS date
# MAGIC
# MAGIC )
# MAGIC
# MAGIC SELECT
# MAGIC     date,
# MAGIC
# MAGIC     -- Year, Quarter and Month
# MAGIC     year(date) AS year,
# MAGIC     quarter(date) AS quarter,
# MAGIC     month(date) AS month,
# MAGIC
# MAGIC     -- Month names
# MAGIC     date_format(date, 'MMMM') AS month_name,
# MAGIC     date_format(date, 'MMM') AS month_short_name,
# MAGIC
# MAGIC     -- Week and Day information
# MAGIC     weekofyear(date) AS week_of_year,
# MAGIC     dayofmonth(date) AS day_of_month,
# MAGIC     dayofweek(date) AS day_of_week,
# MAGIC     date_format(date, 'EEEE') AS day_of_week_name,
# MAGIC     date_format(date, 'EEE') AS day_of_week_short_name,
# MAGIC     dayofyear(date) AS day_of_year,
# MAGIC
# MAGIC     -- Weekend and Weekday
# MAGIC     CASE
# MAGIC         WHEN dayofweek(date) IN (1, 7) THEN TRUE
# MAGIC         ELSE FALSE
# MAGIC     END AS is_weekend,
# MAGIC
# MAGIC     CASE
# MAGIC         WHEN dayofweek(date) NOT IN (1, 7) THEN TRUE
# MAGIC         ELSE FALSE
# MAGIC     END AS is_weekday,
# MAGIC
# MAGIC     -- Year and Month formatting
# MAGIC     concat(year(date), '-Q', quarter(date)) AS year_quarter,
# MAGIC     date_format(date, 'yyyy-MM') AS year_month,
# MAGIC
# MAGIC     -- First and Last day of month
# MAGIC     last_day(date) AS last_day_of_month,
# MAGIC     date = last_day(date) AS is_last_day_of_month,
# MAGIC     date = date_trunc('month', date) AS is_first_day_of_month
# MAGIC
# MAGIC FROM date_range
# MAGIC
# MAGIC ORDER BY date;
# MAGIC