"""
agent_chat.py
Interactive chat interface for the AI agent.
Run with: python app/agent/agent_chat.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agent.agent import run_agent

def is_business_question(question: str) -> bool:
    keywords =[
        "product", "store", "revenue", "sales", "profit",
        "performance", "trend", "month", "category", "worst",
        "best", "top", "selling", "margin", "forecast",
        "underperform", "summary", "how much", "how many",
        "which", "what is", "what are", "show me", "give me"
        "comapre", "analyse", "analyze", "reprot", "recommend",
        "suggest", "why", "explain"
    ]
    return any (k in question.lower() for k in keywords)

if __name__ == "__main__":
    print("=" * 55)
    print(" RetailMind AI Agent")
    print(" Powered by Claude + Tool Calling")
    print(" Type 'quit' to exit")
    print("=" * 55)

    while True:
        print()
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not is_business_question(question):
            print("Assistant: Happy to help! Ask me anything about your retail data.")
            continue

        answer = run_agent(question)
        print(f"\nAssistant: {answer}") 