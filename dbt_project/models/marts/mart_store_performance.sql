-- mart_store_performance.sql
-- Store KPIs — revenue, profit, transaction count

SELECT
    st.store_id,
    st.city,
    st.region,
    st.size_sqm,
    COUNT(s.sale_id)                        AS total_transactions,
    SUM(s.quantity)                         AS units_sold,
    ROUND(SUM(s.sales_amount), 2)           AS total_revenue,
    ROUND(SUM(s.gross_profit), 2)           AS total_profit,
    ROUND(AVG(s.sales_amount), 2)           AS avg_transaction_value,
    ROUND(SUM(s.gross_profit) * 100.0
          / SUM(s.sales_amount), 1)         AS profit_margin_pct
FROM {{ ref('stg_sales') }} s
JOIN {{ ref('stg_stores') }} st
    ON s.store_id = st.store_id
GROUP BY
    st.store_id,
    st.city,
    st.region,
    st.size_sqm
ORDER BY total_revenue DESC