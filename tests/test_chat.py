"""
test_chat.py
Teests for the AI chat assistant.
Note: these tests mock the API calls so they don't
need the server running or real API credits.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest.mock import patch, MagicMock
from app.ai.chat import fetch_relevant_data, build_prompt

def test_fetch_includes_summary_always():
    """ Summary data is always fetched regardless of question."""
    with patch("app.ai.chat.fetch") as mock_fetch:
        mock_fetch.return_value ={"summary": {"total_revenue": 50000}}
        data = fetch_relevant_data("hello")
        # summary endpoint always called
        mock_fetch.assert_any_call("/analytics/summary")

def test_fetch_includes_products_for_product_question():
    """ Product endpoint fetches when question mentions products."""
    with patch("app.ai.chat.fetch") as mock_fetch:
        mock_fetch.return_value = {}
        data = fetch_relevant_data("What are the top selling products?")
        calls = [str(c) for c in mock_fetch.call_args_list]
        assert any("top-products" in c for c in calls)

def test_fetch_includes_stores_for_store_question():
    """Store endpoints fetched when question mentions stores."""
    with patch("app.ai.chat.fetch") as mock_fetch:
        mock_fetch.return_value = {}
        data = fetch_relevant_data("which store is performing worst?")
        calls = [str(c) for c in mock_fetch.call_args_list]
        assert any("store" in c for c in calls)

def test_build_prompt_contains_question():
    """Prompt always contains the user question."""
    prompt = build_prompt("what is revenue?", {"summary": {}})
    assert "what is revenue?" in prompt


def test_build_prompt_contains_data():
    """Prompt contains the data passed to it."""
    data = {"summary": {"total_revenue": 99999}}
    prompt = build_prompt("test question", data)
    assert "99999" in prompt


def test_rag_retrieves_company_context():
    """RAG always returns company context."""
    from app.ai.rag import retrieve_context
    context = retrieve_context("anything")
    assert "RetailMind" in context


def test_rag_retrieves_product_context():
    """RAG returns product context for product questions."""
    from app.ai.rag import retrieve_context
    context = retrieve_context("tell me about dairy products")
    assert "Dairy" in context