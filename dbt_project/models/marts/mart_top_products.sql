-- mart_top_products.sql
-- Top products by revenue — used directly by the AI agent

SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(s.sale_id)                        AS total_transactions,
    SUM(s.quantity)                         AS units_sold,
    ROUND(SUM(s.sales_amount), 2)           AS total_revenue,
    ROUND(SUM(s.gross_profit), 2)           AS total_profit,
    ROUND(AVG(s.sales_amount), 2)           AS avg_transaction_value,
    ROUND(SUM(s.gross_profit) * 100.0
          / SUM(s.sales_amount), 1)         AS profit_margin_pct
FROM {{ ref('stg_sales') }} s
JOIN {{ ref('stg_products') }} p
    ON s.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_revenue DESC