"""
tools.py
Defines every tool the AI agent can call.
Each tool has:
  - A schema (tells Claude what it does and what parameters it takes)
  - An executor function (actually runs the tool)
"""

import httpx # type: ignore

API_BASE = "http://127.0.0.1:8000"

def fetch(endpoint: str, params: dict = None) -> dict:
    """ Call the FastAPI endpoint and return JSON """
    try:
        r = httpx.get(f"{API_BASE}{endpoint}", params = params, timeout=10)
        return r.json()
    except Exception as e:
        return{"error": str(e)}
    
# Tool definations
# These are sent to claude so it knows what tools exist
# and exactly how to call them

TOOL_DEFINATIONS =[
    { 
        "name": "get_top_products",
        "description": (
            "Get the top selling products by revenue. "
            "Use this when asked about best seller, top products, "
            "popular item, or product performance."
        ),
        "input_schema": {
            "type": "object",
            "properties":{
                "limit": {
                    "type": "integer",
                    "description": " Number of products to return (default 10)",
                },
                "category": {
                    "type": "string",
                    "description":(
                        "Filter by category: Dairy, Bakery, "
                        " Meat, seafood, or Pantry"
                    ),
                },
            }, 
            "required":[] 
        },

    },
    {
        "name": "get_store_performance",
        "description": (
            "Get revenue, profit and transaction data for each store."
            "Use this when asked about store performance, locations,"
            " Underperforming stores, or regional analysis. "
        ),
        "input_schema":{
            "type": "object",
            "properties":{
                "region": {
                    "type": "string",
                    "description": "Filter by region: North Island or South Island",
                },
            },
            "required":[],
        },
    },
    {
        "name": "get_monthly_trend",
        "description":(
            "Get monthly revenue and profit trends over time. "
            "Use this when asked trends, growth, monthly performance, "
            " or time-based analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_category_breakdown",
        "description": (
            "Get sales and profit mrgin breakdown by product category. "
            "Use this when asked about categories, margins, "
            "or which category is most profitable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_underperforming_stores",
        "description": (
            "Get stores that are earning below 80% of average revenue. "
            "Use this when asked about weak stores, problems, "
            "or stores that need attention."
        ),
        "input_schema":{
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_business_summary",
        "description": (
            "Get an overall summary of the entries business - "
            "total revenu, profit, transactions, data range."
        ),
        "input_schema": {
            "type": "object",
            "properties":{},
            "required": [],
        },
    },
]    

# Tool Executors
# These actually runs when claude decieds to call a tool 

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """ 
    Run the tool claude requested and return the result as a string.
    Claude receives this result and uses it in its next reasoning step.
    """

    if tool_name == "get_top_products":
        result = fetch("/analytics/top-products", params=tool_input)
    
    elif tool_name == "get_store_performance":
        result = fetch("/analytics/store-performance", params=tool_input)
    
    elif tool_name == "get_monthly_trend":
        result = fetch("/analytics/monthly-trend")
    
    elif tool_name == "get_category_breakdown":
        result = fetch("/analytics/category-breakdown")

    elif tool_name == "get_underperforming_stores":
        result = fetch("/analytics/underperforming-stores")
    
    elif tool_name == "get_business_summary":
        result = fetch("/analytics/summary")

    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return str(result)
