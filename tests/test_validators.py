"""
test_validators.py
Unit tests for every validation rule.
Run with: python -m pytest tests/ -v
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ingestion.validators import (
    ValidationReport,
    check_nulls,
    check_types,
    check_ranges,
    check_duplicates,
    check_referential_integrity,
)


def make_report():
    return ValidationReport(table_name="test", total_rows=10)


# ── Null checks ───────────────────────────────────────────────────────

def test_null_check_drops_missing_rows():
    df = pd.DataFrame({
        "sale_id":      ["A", "B", None, "D"],
        "sales_amount": [10,   20,  30,   40],
    })
    result = check_nulls(df, ["sale_id"], make_report())
    assert len(result) == 3

def test_null_check_passes_clean_data():
    df = pd.DataFrame({"sale_id": ["A","B","C"], "qty": [1,2,3]})
    result = check_nulls(df, ["sale_id"], make_report())
    assert len(result) == 3


# ── Type checks ───────────────────────────────────────────────────────

def test_type_check_drops_invalid_float():
    df = pd.DataFrame({"amount": ["10.50", "20.00", "bad_value"]})
    result = check_types(df, {"amount": float}, make_report())
    assert len(result) == 2

def test_type_check_passes_valid_numbers():
    df = pd.DataFrame({"quantity": ["3","5","10"]})
    result = check_types(df, {"quantity": int}, make_report())
    assert len(result) == 3


# ── Range checks ──────────────────────────────────────────────────────

def test_range_check_drops_negative_quantity():
    df = pd.DataFrame({"quantity": [5, -3, 10, 0]})
    result = check_ranges(df, {"quantity": (1, 1000)}, make_report())
    assert len(result) == 2

def test_range_check_drops_zero_amount():
    df = pd.DataFrame({"sales_amount": [10.0, 0.0, 25.5, -5.0]})
    result = check_ranges(df, {"sales_amount": (0.01, 100000)}, make_report())
    assert len(result) == 2


# ── Duplicate checks ──────────────────────────────────────────────────

def test_duplicate_check_removes_dupes():
    df = pd.DataFrame({
        "sale_id": ["A","B","A","C"],
        "amount":  [10,  20,  10,  30]
    })
    result = check_duplicates(df, ["sale_id"], make_report())
    assert len(result) == 3

def test_duplicate_check_passes_unique_data():
    df = pd.DataFrame({"sale_id": ["A","B","C"]})
    result = check_duplicates(df, ["sale_id"], make_report())
    assert len(result) == 3


# ── Referential integrity ─────────────────────────────────────────────

def test_ref_integrity_drops_unknown_ids():
    df    = pd.DataFrame({"product_id": ["P001","P002","P999"]})
    valid = {"P001","P002","P003"}
    result = check_referential_integrity(df, "product_id", valid, make_report())
    assert len(result) == 2
    assert "P999" not in result["product_id"].values

def test_ref_integrity_passes_known_ids():
    df    = pd.DataFrame({"store_id": ["S01","S02"]})
    valid = {"S01","S02","S03"}
    result = check_referential_integrity(df, "store_id", valid, make_report())
    assert len(result) == 2