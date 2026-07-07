"""
test_agent.py
Tests for the AI agent tools.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest import result
from unittest.mock import patch
from app.agent.tools import execute_tool, TOOL_DEFINATIONS

def test_all_tools_have_required_fields():
    """ Every tool defination must have name, description, input_schema. """
    for tool in TOOL_DEFINATIONS:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool

def test_tool_definations_count():
    """ Should have exactly 6 tools defined."""
    assert len(TOOL_DEFINATIONS) == 6

def test_execute_unknown_tool_returns_error():
    """Calling an unknown tool returns an error, not a crash."""
    result = execute_tool("nonexistent_tool", {})
    assert "error" in result.lower() or "Unknown" in result


def test_execute_tool_calls_correct_endpoint():
    """get_top_products tool calls the right API endpoint."""
    with patch("app.agent.tools.fetch") as mock_fetch:
        mock_fetch.return_value = {"data": []}
        execute_tool("get_top_products", {"limit": 5})
        mock_fetch.assert_called_with(
            "/analytics/top-products", params={"limit": 5}
        )


def test_execute_summary_tool():
    """get_business_summary calls the summary endpoint."""
    with patch("app.agent.tools.fetch") as mock_fetch:
        mock_fetch.return_value = {"summary": {}}
        execute_tool("get_business_summary", {})
        mock_fetch.assert_called_with("/analytics/summary")

