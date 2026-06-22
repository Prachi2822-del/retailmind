{{ config(materialized='table') }}

select
    date,
    store_id,
    sum(sales_amount)  as total_revenue,
    sum(gross_profit)  as total_profit,
    sum(quantity)      as total_units
from {{ ref('stg_sales') }}
group by date, store_id
