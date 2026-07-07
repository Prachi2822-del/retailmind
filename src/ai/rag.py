"""
rag.py
Simple rag implementation.
STores business knowledge that supplements live warehouse data.
The AI uses this context alongside live numbers to give better answers.
"""

# Business knowledge base - in production this would be
# Stired in a vector database like pinecone or pgvector
KNOWLEDGE_BASE = {
    "company": """ 
    RetailMind is a New Zealand supermarket chain with 5 stores
    Across North Island and South Island.
    Stores: Auckland CBD, Wellington, Christchurch, Hamilton, Tauranga.
    Product categories: Dairy, Bakery, Meat, seafood, Pantry.
    Financial year runs January to December.
    Target profit margin is 25% across all categories.
""",

"kpis": """
    Key performance indicatores:
    - Revenue per store per month target: NZD 15,000
    - Average transaction value target: NZD 8.00
    - Gross profit margin target: 25%
    - Underperforming threshould: below 80% of average store revenue
    - Stock turn target: 12x per year for perishables
    """,

"products": """
    Top product lines by strategic importance:
    - Dairy: highest volume, low margin, essential category
    - Meat: highest margin, moderate volume
    - Seafood: premium category, high margin
    - Pantry: steady demand, good margings
    """,

"regions": """
    Regional context:
    - North Island stores( Auckland, Wellington, Hamilton, Tauranga):
      Higher population density, more competition
    - South Island stores( Christchurch):
      Lower competition, strong community loyality
    - Auckland CBD: highest foot traffic, premium pricing possible
    """
}

def retrieve_context(question: str) -> str:
    """ 
    Retrieve relevant knowledge base entries for a question.
    In phase 6 this becomes a proper vector similarity search.
    """
    question_lower = question.lower()
    relevant =[]

    # Always include company context
    relevant.append (KNOWLEDGE_BASE["company"])

    if any(w in question_lower for w in ["kpi", "target", "performance", "margin", "benchmark"]):
        relevant.append(KNOWLEDGE_BASE["kpis"])
    
    if any(w in question_lower for w in ["product", "category", "dairy", "meat", "bakery", "seafood"]):
        relevant.append(KNOWLEDGE_BASE["products"])

    if any(w in question_lower for w in ["store", "region", "island", "auckland", "wellington"]):
        relevant.append(KNOWLEDGE_BASE["regions"])

    return "\n\n".join(relevant)

def ask_with_rag(question: str, live_data: dict, client, model: str) -> str:
    """
    Enhanced answer using both RAG context and live data.
    Called by the agent in phase 6.
    """
    context = retrieve_context(question)
    prompt = f""" You are a retail analytics assistant for aa New Xeeland supermarket chain.

company knowledge:
{context}

live warehouse data: 
{live_data}

User question: {question}

Answer clearly and concisely in 3-5 sentences.
Reference specific numbers from the live data.
Compare against targets from the company knowledge where relevant.
"""
    response = client.message.create(
        model=model,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text