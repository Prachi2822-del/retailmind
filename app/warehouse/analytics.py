"""
analytics.py
Pre-built analytical queries that run against the star schema.
These are the queries the AI agent will call in Phase 6.
"""

import sqlite3
import pandas as pd

DB_PATH = "retailmind.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def top_products(limit=10, category=None):
    """Top products by total revenue."""
    conn = get_connection()
    where = f"AND p.category = '{category}'" if category else ""
    query = f"""
        SELECT
            p.product_name,
            p.category,
            SUM(f.quantity)     AS units_sold,
            ROUND(SUM(f.sales_amount), 2) AS total_revenue,
            ROUND(SUM(f.gross_profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        WHERE 1=1 {where}
        GROUP BY p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT {limit}
    """
    result = pd.read_sql(query, conn)
    conn.close()
    return result


def store_performance(region=None):
    """Revenue and profit by store with month-over-month comparison."""
    conn = get_connection()
    where = f"AND s.region = '{region}'" if region else ""
    query = f"""
        SELECT
            s.city,
            s.region,
            COUNT(f.sale_id)              AS total_transactions,
            SUM(f.quantity)               AS units_sold,
            ROUND(SUM(f.sales_amount), 2) AS total_revenue,
            ROUND(SUM(f.gross_profit), 2) AS total_profit,
            ROUND(AVG(f.sales_amount), 2) AS avg_transaction_value
        FROM fact_sales f
        JOIN dim_store s ON f.store_id = s.store_id
        WHERE 1=1 {where}
        GROUP BY s.city, s.region
        ORDER BY total_revenue DESC
    """
    result = pd.read_sql(query, conn)
    conn.close()
    return result


def monthly_revenue_trend():
    """Revenue trend by month — used for forecasting and anomaly detection."""
    conn = get_connection()
    query = """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(f.sale_id)              AS transactions,
            ROUND(SUM(f.sales_amount), 2) AS revenue,
            ROUND(SUM(f.gross_profit), 2) AS profit,
            ROUND(AVG(f.sales_amount), 2) AS avg_sale
        FROM fact_sales f
        JOIN dim_date d ON f.date = d.date
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    """
    result = pd.read_sql(query, conn)
    conn.close()
    return result


def category_breakdown():
    """Sales split by product category."""
    conn = get_connection()
    query = """
        SELECT
            p.category,
            COUNT(f.sale_id)              AS transactions,
            ROUND(SUM(f.sales_amount), 2) AS revenue,
            ROUND(SUM(f.gross_profit), 2) AS profit,
            ROUND(SUM(f.gross_profit) * 100.0
                  / SUM(f.sales_amount), 1) AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """
    result = pd.read_sql(query, conn)
    conn.close()
    return result


def underperforming_stores(threshold=0.8):
    """Stores earning below threshold × average revenue — flagged for review."""
    conn = get_connection()
    query = f"""
        WITH store_rev AS (
            SELECT
                s.city,
                s.region,
                ROUND(SUM(f.sales_amount), 2) AS revenue
            FROM fact_sales f
            JOIN dim_store s ON f.store_id = s.store_id
            GROUP BY s.city, s.region
        ),
        avg_rev AS (
            SELECT AVG(revenue) AS avg_revenue FROM store_rev
        )
        SELECT
            sr.city,
            sr.region,
            sr.revenue,
            ROUND(ar.avg_revenue, 2)    AS avg_revenue,
            ROUND(sr.revenue * 100.0
                  / ar.avg_revenue, 1)  AS pct_of_average
        FROM store_rev sr, avg_rev ar
        WHERE sr.revenue < ar.avg_revenue * {threshold}
        ORDER BY pct_of_average ASC
    """
    result = pd.read_sql(query, conn)
    conn.close()
    return result


if __name__ == "__main__":
    print("Top 5 products:")
    print(top_products(5).to_string(index=False))

    print("\nStore performance:")
    print(store_performance().to_string(index=False))

    print("\nMonthly revenue trend:")
    print(monthly_revenue_trend().to_string(index=False))

    print("\nCategory breakdown:")
    print(category_breakdown().to_string(index=False))

    print("\nUnderperforming stores:")
    print(underperforming_stores().to_string(index=False))