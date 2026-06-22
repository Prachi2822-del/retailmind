"""
star_schema.py
Builds the dimensional model (star schema) inside SQLite.
Reads from raw tables → creates fact + dimension tables.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "retailmind.db"


def build_dim_date(conn):
    """Dimension table: every date in the dataset with calendar attributes."""
    print("  Building dim_date...")
    query = "SELECT DISTINCT date FROM sales ORDER BY date"
    dates = pd.read_sql(query, conn)

    dates["date"]        = pd.to_datetime(dates["date"])
    dates["year"]        = dates["date"].dt.year
    dates["quarter"]     = dates["date"].dt.quarter
    dates["month"]       = dates["date"].dt.month
    dates["month_name"]  = dates["date"].dt.strftime("%B")
    dates["week"]        = dates["date"].dt.isocalendar().week.astype(int)
    dates["day_of_week"] = dates["date"].dt.strftime("%A")
    dates["is_weekend"]  = dates["date"].dt.dayofweek >= 5
    dates["date"]        = dates["date"].dt.strftime("%Y-%m-%d")

    dates.to_sql("dim_date", conn, if_exists="replace", index=False)
    print(f"    {len(dates)} date rows created")


def build_dim_product(conn):
    """Dimension table: product details."""
    print("  Building dim_product...")
    df = pd.read_sql("SELECT * FROM products", conn)
    df = df.rename(columns={"name": "product_name"})
    df.to_sql("dim_product", conn, if_exists="replace", index=False)
    print(f"    {len(df)} products loaded")


def build_dim_store(conn):
    """Dimension table: store details."""
    print("  Building dim_store...")
    df = pd.read_sql("SELECT * FROM stores", conn)
    df.to_sql("dim_store", conn, if_exists="replace", index=False)
    print(f"    {len(df)} stores loaded")


def build_dim_customer(conn):
    """Dimension table: customer details (PII masked for safety)."""
    print("  Building dim_customer...")
    df = pd.read_sql("SELECT * FROM customers", conn)
    # Mask PII — never expose real emails in analytics layer
    df["email"] = df["email"].apply(
        lambda e: e[0] + "***@" + e.split("@")[1] if pd.notna(e) else e
    )
    df.to_sql("dim_customer", conn, if_exists="replace", index=False)
    print(f"    {len(df)} customers loaded (email PII masked)")


def build_fact_sales(conn):
    """
    Fact table: one row per sale with all foreign keys + measures.
    This is the centre of the star schema.
    """
    print("  Building fact_sales...")
    df = pd.read_sql("SELECT * FROM sales", conn)

    # Keep only the columns needed in the fact table
    fact = df[[
        "sale_id",
        "date",
        "product_id",
        "store_id",
        "customer_id",
        "quantity",
        "sales_amount",
        "gross_profit",
    ]].copy()

    fact.to_sql("fact_sales", conn, if_exists="replace", index=False)
    print(f"    {len(fact):,} fact rows created")


def run_quality_checks(conn):
    """Verify the star schema was built correctly."""
    print("\n  Running quality checks...")
    checks = {
        "fact_sales row count":   "SELECT COUNT(*) FROM fact_sales",
        "dim_product count":      "SELECT COUNT(*) FROM dim_product",
        "dim_store count":        "SELECT COUNT(*) FROM dim_store",
        "dim_date count":         "SELECT COUNT(*) FROM dim_date",
        "dim_customer count":     "SELECT COUNT(*) FROM dim_customer",
        "Null sale_ids in fact":  "SELECT COUNT(*) FROM fact_sales WHERE sale_id IS NULL",
        "Orphan product_ids":     """
            SELECT COUNT(*) FROM fact_sales
            WHERE product_id NOT IN (SELECT product_id FROM dim_product)
        """,
    }
    all_passed = True
    for name, query in checks.items():
        result = conn.execute(query).fetchone()[0]
        status = "✓" if ("Null" not in name and "Orphan" not in name) or result == 0 else "✗"
        if status == "✗":
            all_passed = False
        print(f"    {status}  {name}: {result}")
    return all_passed


def build_star_schema():
    print("=" * 55)
    print("  Building Star Schema")
    print("=" * 55)

    conn = sqlite3.connect(DB_PATH)

    print("\nBuilding dimension tables...")
    build_dim_date(conn)
    build_dim_product(conn)
    build_dim_store(conn)
    build_dim_customer(conn)

    print("\nBuilding fact table...")
    build_fact_sales(conn)

    passed = run_quality_checks(conn)
    conn.close()

    print("\nStar schema complete ✓" if passed else "\nSome checks failed — review above")
    print("=" * 55)


if __name__ == "__main__":
    build_star_schema()