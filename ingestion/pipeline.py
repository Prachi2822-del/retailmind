"""
pipeline.py
Runs the full ETL pipeline:
  Extract  → read CSVs from data/raw/
  Transform → validate with validators.py
  Load      → save clean data to SQLite + upload to S3
"""

import os
import sys
import sqlite3
import pandas as pd
import boto3
from botocore.exceptions import BotoCoreError, ClientError

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ingestion.validators import (
    ValidationReport,
    check_nulls,
    check_types,
    check_ranges,
    check_duplicates,
    check_referential_integrity,
)

S3_BUCKET = "retailmind-prachi-2026"
DB_PATH   = "retailmind.db"


# ── EXTRACT ──────────────────────────────────────────────────────────────

def extract(data_dir="data/raw"):
    print("EXTRACT: Reading source files...")
    tables = ["sales", "products", "stores", "customers"]
    dfs = {}
    for name in tables:
        path = f"{data_dir}/{name}.csv"
        df = pd.read_csv(path)
        print(f"  {name:12s}: {len(df):,} rows")
        dfs[name] = df
    return dfs


# ── TRANSFORM ────────────────────────────────────────────────────────────

def transform_sales(df, products_df, stores_df):
    report = ValidationReport(table_name="sales", total_rows=len(df))
    print(f"\nTRANSFORM: Validating sales ({len(df):,} rows)...")

    df = check_nulls(df,
        required_cols=["sale_id","date","store_id",
                       "product_id","quantity","sales_amount"],
        report=report)

    df = check_types(df,
        type_map={"quantity": int, "sales_amount": float},
        report=report)

    df = check_ranges(df,
        range_map={"quantity": (1, 1000), "sales_amount": (0.01, 100_000)},
        report=report)

    df = check_duplicates(df, key_cols=["sale_id"], report=report)

    df = check_referential_integrity(
        df, "product_id", set(products_df["product_id"]), report, "products")
    df = check_referential_integrity(
        df, "store_id", set(stores_df["store_id"]), report, "stores")

    # Add gross_profit column
    df = df.merge(products_df[["product_id","cost_price"]], on="product_id", how="left")
    df["gross_profit"] = (df["sales_amount"] - df["quantity"] * df["cost_price"]).round(2)

    report.passed_rows = len(df)
    report.failed_rows = report.total_rows - report.passed_rows
    return df, report


def transform(dfs):
    cleaned, reports = {}, {}
    cleaned["sales"], reports["sales"] = transform_sales(
        dfs["sales"], dfs["products"], dfs["stores"]
    )
    cleaned["products"]  = dfs["products"]
    cleaned["stores"]    = dfs["stores"]
    cleaned["customers"] = dfs["customers"]
    return cleaned, reports


# ── LOAD: SQLite ─────────────────────────────────────────────────────────

def load_sqlite(cleaned):
    print(f"\nLOAD: Writing to SQLite ({DB_PATH})...")
    conn = sqlite3.connect(DB_PATH)
    for name, df in cleaned.items():
        df.to_sql(name, conn, if_exists="replace", index=False)
        print(f"  {name:12s}: {len(df):,} rows → SQLite table '{name}'")
    conn.close()


# ── LOAD: S3 ─────────────────────────────────────────────────────────────

def load_s3(cleaned):
    print(f"\nLOAD: Uploading clean CSVs to S3 ({S3_BUCKET})...")
    s3 = boto3.client("s3")
    os.makedirs("data/processed", exist_ok=True)

    for name, df in cleaned.items():
        local_path = f"data/processed/{name}_clean.csv"
        df.to_csv(local_path, index=False)
        s3_key = f"processed/{name}_clean.csv"
        try:
            s3.upload_file(local_path, S3_BUCKET, s3_key)
            print(f"  {name:12s}: uploaded → s3://{S3_BUCKET}/{s3_key}")
        except (BotoCoreError, ClientError) as e:
            print(f"  {name:12s}: S3 upload failed — {e}")


# ── MAIN ─────────────────────────────────────────────────────────────────

def run_pipeline():
    print("=" * 55)
    print("  RetailMind ETL Pipeline")
    print("=" * 55)

    dfs              = extract()
    cleaned, reports = transform(dfs)

    # Print validation report
    print("\nVALIDATION REPORT:")
    print("-" * 55)
    for table, r in reports.items():
        print(f"  {r.table_name}")
        print(f"    Total rows : {r.total_rows:,}")
        print(f"    Passed     : {r.passed_rows:,}  ({r.pass_rate}%)")
        print(f"    Rejected   : {r.failed_rows:,}")
        for issue in r.issues:
            print(f"    ⚠  {issue}")

    load_sqlite(cleaned)
    load_s3(cleaned)

    print("\nPipeline complete ✓")
    print("=" * 55)


if __name__ == "__main__":
    run_pipeline()