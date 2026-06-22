-- stg_products.sql
SELECT
    product_id,
    product_name,
    category,
    CAST(cost_price AS REAL) AS cost_price,
    is_active
FROM main.dim_product