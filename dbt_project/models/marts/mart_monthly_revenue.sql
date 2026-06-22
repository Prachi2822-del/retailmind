-- mart_monthly_revenue.sql
-- Monthly revenue trend — used for forecasting

SELECT
    d.year,
    d.month,
    d.month_name,
    d.quarter,
    COUNT(s.sale_id)                AS total_transactions,
    SUM(s.quantity)                 AS units_sold,
    ROUND(SUM(s.sales_amount), 2)   AS revenue,
    ROUND(SUM(s.gross_profit), 2)   AS profit,
    ROUND(AVG(s.sales_amount), 2)   AS avg_sale_value
FROM {{ ref('stg_sales') }} s
JOIN main.dim_date d
    ON s.date = d.date
GROUP BY
    d.year,
    d.month,
    d.month_name,
    d.quarter
ORDER BY
    d.year,
    d.month