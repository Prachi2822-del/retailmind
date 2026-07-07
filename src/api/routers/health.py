"""
health.py
Health check endpoint - confirms API and database are reachable.
"""

from fastapi import APIRouter
import sqlite3

router = APIRouter(prefix="/health", tags=["health"])

DB_PATH = "retailmind.db"

@router.get("/")
def health_check():
    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]
        conn.close()
        return{
            "status": "healthy",
            "database": "reachable",
            "sales_count": count
        }
    except Exception as e:
        return{
            "status": "unhealthy",
            "error": str(e)
        }