
"""
main.py
Fast.API application entry point
Run with: uvicorn app.api.main:app --reload
"""

from fastapi import FastAPI
from src.api.routers import analytics, health

app = FastAPI(
    title="RetailMind API",
    description="Retail analytics API powering the AI agent",
    version="1.0.0"
)

app.include_router(health.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return{
        "project":"RetailMind",
        "status": "running",
        "docs": "/docs"
    }