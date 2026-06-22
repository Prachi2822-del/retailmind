-- stg_sales.sql
-- Staging layer: clean column names, cast types, add row quality flag

SELECT
    sale_id,
    date,
    store_id,
    product_id,
    customer_id,
    CAST(quantity AS INTEGER)      AS quantity,
    CAST(sales_amount AS REAL)     AS sales_amount,
    CAST(gross_profit AS REAL)     AS gross_profit,
    CASE
        WHEN sales_amount > 0 AND quantity > 0 THEN 'valid'
        ELSE 'suspect'
    END AS row_quality
FROM main.sales
WHERE sale_id IS NOT NULL