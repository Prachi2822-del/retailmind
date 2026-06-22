-- stg_stores.sql
SELECT
    store_id,
    city,
    region,
    CAST(size_sqm AS INTEGER) AS size_sqm
FROM main.dim_store