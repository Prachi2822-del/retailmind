"""
analytics.py
All retail analytics endpoints.
These are called by the AI agent in phase 6.
"""

from fastapi import APIRouter, Query
import sqlite3
import pandas as pd

router = APIRouter (prefix = "/analytics", tags=["analytics"])
DB_PATH = "retailmind.db"

def query_db(sql: str) -> list[dict]:
    """ Run a SQL query and return results as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    result = pd.read_sql(sql, conn).to_dict(orient = "records")
    conn.close()
    return result

@router.get("/top-products")
def top_products(
    limit: int = Query(19, ge=1, le=50),
    category: str = Query(None)
):
    """Top products by total revenue."""
    where = f"AND p.category = '{category}'" if category else ""
    sql = f""" 
        SELECT
            p.name,
            p.category,
            SUM(s.quantity) as total_units,
            ROUND(SUM(s.sales_amount), 2) as total_revenue,
            ROUND(SUM(s.gross_profit), 2) as total_profit,
            ROUND(AVG(s.sales_amount), 2) as avg_sale
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE 1=1 {where}
        GROUP BY p.name, p.category
        ORDER BY total_revenue DESC
        LIMIT {limit}
    """
    return{"data": query_db(sql), "count": limit}

@router.get("/store-performance")
def store_performance(
    region: str = Query(None)
):
    """Revenuew =and profit by store."""
    where = f"AND s.region = '{region}' " if region else ""
    sql = f"""
        SELECT
            s.city,
            s.region,
            COUNT(f.sale_id) as total_sales,
            ROUND(SUM(f.sales_amount), 2) as total_revenue,
            ROUND(SUM(f.gross_profit), 2) as total_profit,
            ROUND(AVG(f.sales_amount), 2) as avg_sale
        FROM sales f
        JOIN stores s ON f.store_id = s.store_id
        WHERE 1=1 {where}
        GROUP BY s.city, s.region
        ORDER BY total_revenue DESC
    """
    return{"data": query_db(sql)}

@router.get("/monthly-trend")
def monthly_trend():
    sql = """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(f.sale_id) as total_sales,
            ROUND(SUM(f.sales_amount), 2) as total_revenue,
            ROUND(SUM(f.gross_profit), 2) as total_profit,
            ROUND(AVG(f.sales_amount), 2) as avg_sale
        FROM sales f
        JOIN dim_date d ON f.date = d.date
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    """
    return {"data": query_db(sql)}

@router.get("/category-breakdown")
def category_breakdown():
    """ Sales and profit split by product category."""
    sql = """
        SELECT
            p.category,
            COUNT(f.sale_id) AS transaction_count,
            ROUND(SUM(f.sales_amount), 2) AS revenue,
            ROUND(SUM(f.gross_profit), 2) AS gross_profit,
            ROUND(SUM(f.gross_profit) * 100.0 / SUM(f.sales_amount), 1) AS gross_margin_pct
        FROM sales f
        JOIN products p ON f.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """
    return {"data": query_db(sql)}

@router.get("/underperforming-stores")
def underperforming_stores():
    sql = """
        WITH store_rev AS (
            SELECT
                s.city,
                s.region,
                ROUND(SUM(f.sales_amount), 2) as revenue
            FROM sales f
            JOIN stores s ON f.store_id = s.store_id
            GROUP BY s.city, s.region
        ),
        avg_rev AS (
            SELECT AVG(revenue) AS avg_revenue FROM store_rev
        )
        SELECT
            sr.city,
            sr.region,
            sr.revenue,
            ROUND(ar.avg_revenue, 2) as avg_revenue,
            ROUND(sr.revenue * 100.0 / ar.avg_revenue, 1) as pct_of_average
        FROM store_rev sr, avg_rev ar
        WHERE sr.revenue < ar.avg_revenue * 0.8
        ORDER BY pct_of_average ASC
    """
    return {"data": query_db(sql)}

@router.get("/summary")
def summary():
    sql = """
        SELECT
            COUNT(sale_id) as total_sales,
            ROUND(SUM(sales_amount), 2) as total_revenue,
            ROUND(SUM(gross_profit), 2) as total_profit,
            ROUND(AVG(sales_amount), 2) as avg_sale,
            COUNT(DISTINCT product_id) as unique_products,
            COUNT(DISTINCT store_id) as unique_stores,
            MIN(date) as first_sale,
            MAX(date) as last_sale
        FROM sales
    """
    rows = query_db(sql)
    return {"summary": rows[0] if rows else {}}
