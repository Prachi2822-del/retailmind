"""
chat.py
Ai chat assistant that answer retail questions using liove warehouse data.

Flow:
User question -> classify intent (which data is needed?) -> Fetch data from FastAPI endpoints -> send question + data to claude -> Return plan english answer 
"""

import os
import httpx
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
APi_BASE = "http://127.0.0.1:8000"
MODEL = "claude-sonnet-4-6"

# Data Fetching

def fetch (endpoint: str, params: dict = None) -> dict:
    """
    Call FastAPI endpoint and return the JSON response.
    """
    try:
        r = httpx.get(f"{APi_BASE}{endpoint}", params=params, timeout = 10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}
    

def fetch_relevant_data(question: str) -> dict:
    """ 
    Look at the quetsion and decide which endpoints to call.
    This is simple intent detection - the AI agent in phase 6
    will do this intelligently using tool caling.
    """
    question_lower = question.lower()
    data ={}

    # ALways fetch the summary for context
    data["summary"] = fetch("/analytics/summary")

    if any(word in question_lower for word in 
           ["product", "selling", "item", "milk", "bread",
            " category", "dairy", "bakery", " meat"]):
        data["top_products"] = fetch("/analytics/top-products")
        data["category_breakdown"] = fetch("/analytics/category-breakdown")

    if any (word in question_lower for word in
            ["store", "location", "city", "auckland", "wellington",
             "christchurch", "hamilton", "tauranga", "region"]):
        data["store_performance"] = fetch("/analytics/store-performance")
        data["underperforming_stores"] = fetch("/analytics/underperforming-stores")

    if any(word in question_lower for word in
           ["month", "trend", "revenue", "growth",
            "January", "february", "march", "time", "period"]):
        data["monthly_trend"] = fetch("/analytics/monthly-trend")
    
    return data

# AI answer generation

def build_prompt(question: str, data:dict) -> str:
    """ Build the prompt that gets send to claude."""
    return f""" You are a retail analytics assistant for a NEW Zealand supermarket chain. 
    you have access to live sales data the warehouse.

User question: {question}
Live data from the warehouse:
{data}

Instructions:
- Answer the question directly and cleaarly
- Reference specific numbers from the data
- Keep your answer to 3-5 sentences maximum
- If the data doesn't contain what's needed to answer, say so honestly
- Use NZD for currency amounts
- Sounds like a helpful business analytics, not a robot.
"""

SMALL_TALK = [
    "hi", "hello", "hey", "thanks", "thank you", "thank",
    "done", "bye", "goodbye", "ok", "okay", "great", "cool",
    "good", "nice", "awesome", "perfect", "got it", "sure"
]

def is_business_question(question: str) -> bool:
    """
    Returns True only if the question is asking for actual data.
    Everything else is treated as conversation.
    """
    business_keywords = [
        "product", "store", "revenue", "sales", "profit",
        "performance", "trend", "month", "category", "worst",
        "best", "top", "selling", "margin", "stock", "forecast",
        "underperform", "summary", "how much", "how many",
        "which", "what is", "what are", "show me", "give me",
        "compare", "analyse", "analyze", "report"
    ]
    q = question.lower()
    return any(keyword in q for keyword in business_keywords)


def ask(question: str) -> dict:
    """
    Main function — takes a question, fetches data, returns AI answer.
    Only fetches warehouse data for real business questions.
    """

    # Not a business question — reply conversationally, no data fetch
    if not is_business_question(question):
        response = client.messages.create(
            model=MODEL,
            max_tokens=30,
            system="You are a friendly assistant. Reply in one sentence only. Never mention data, sales, revenue or business metrics.",
            messages=[{"role": "user", "content": question}]
        )
        return {
            "question":  question,
            "answer":    response.content[0].text,
            "data_used": [],
        }

    # Real business question — fetch data and answer properly
    print(f"\nQuestion: {question}")
    print("Fetching data...")
    data = fetch_relevant_data(question)

    print("Asking Claude...")
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{
            "role":    "user",
            "content": build_prompt(question, data)
        }]
    )

    return {
        "question":  question,
        "answer":    response.content[0].text,
        "data_used": list(data.keys()),
    }

# Test it directly

if __name__ == "__main__":
    print("=" * 55)
    print("  RetailMind AI Assistant")
    print("  Type your question and press Enter")
    print("  Type 'quit' to exit")
    print("=" * 55)

    while True:
        print()
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        result = ask(question)
        print(f"\nAssistant: {result['answer']}")

