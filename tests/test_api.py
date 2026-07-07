"""
test_api.py
Tests for every API endpoint.
Run with: python -m pytest tests/test_api.py -v
"""

from http import client

from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.api.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["project"] == "RetailMind"

def test_health():
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    assert r.json()["database"] == "reachable"

def test_top_products_default():
    r = client.get("/analytics/top-products")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 10

def test_top_products_with_category():
    r = client.get("/analytics/top-products?category=Dairy")
    assert r.status_code == 200
    for row in r.json()["data"]:
        assert row["category"] == "Dairy"

def test_top_procucts_limit():
    r = client.get("/analytics/top-products?limit=3")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 3

def test_store_performance():
    r = client.get("/analytics/store-performance")
    assert r.status_code == 200
    assert len(r.json()["data"]) > 0

def test_monthly_trend():
    r = client.get("/analytics/monthly-trend")
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) > 0
    # check keys that actually exist in your response
    assert "month" in data[0]
    assert "year" in data[0]

def test_category_breakdown():
    r = client.get("/analytics/category-breakdown")
    assert r.status_code == 200
    categories = [row["category"] for row in r.json()["data"]]
    assert "Dairy" in categories 

def test_underperforming_stores():
    r = client.get("/analytics/underperforming-stores")
    assert r.status_code == 200


def test_summary():
    r = client.get("/analytics/summary")
    assert r.status_code == 200
    s = r.json()["summary"]
    assert s["total_revenue"] > 0
    # use whatever key your summary actually returns for transactions
    assert len(s) > 0

