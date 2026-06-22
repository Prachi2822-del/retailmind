{{ config(materialized='view') }}

select
    sale_id,
    date,
    product_id,
    store_id,
    customer_id,
    quantity,
    sales_amount,
    gross_profit
from main.fact_sales
