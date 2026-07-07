"""
app.py
Streamlit dashboard for RetailMind.
Run with: streamlit run streamlit_app/app.py
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.agent.agent import run_agent

import streamlit as st # pyright: ignore[reportMissingImports]
import plotly.express as px # pyright: ignore[reportMissingImports]
import pandas as pd
import sqlite3

DB_PATH = "retailmind.db"

# ── Page config ───────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RetailMind",
    page_icon="🛒",
    layout="wide"
)

# ── Helper ────────────────────────────────────────────────────────────────

def query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(sql, conn)
    conn.close()
    return df


def is_business_question(q: str) -> bool:
    keywords = [
        "product", "store", "revenue", "sales", "profit",
        "performance", "trend", "month", "category", "worst",
        "best", "top", "selling", "margin", "forecast",
        "underperform", "summary", "how much", "how many",
        "which", "what", "show", "give", "compare", "recommend",
        "suggest", "why", "explain", "analyse", "analyze"
    ]
    return any(k in q.lower() for k in keywords)


# ── Sidebar ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🛒 RetailMind")
    st.caption("Retail Analytics Platform")
    st.divider()

    revenue      = query("SELECT ROUND(SUM(sales_amount),2) AS r FROM fact_sales").iloc[0,0] or 0
    profit       = query("SELECT ROUND(SUM(gross_profit),2) AS p FROM fact_sales").iloc[0,0] or 0
    transactions = query("SELECT COUNT(*) AS c FROM fact_sales").iloc[0,0] or 0
    stores       = query("SELECT COUNT(*) AS s FROM dim_store").iloc[0,0] or 0
    
    st.metric("Total Revenue",      f"NZD ${revenue:,.2f}")
    st.metric("Total Profit",       f"NZD ${profit:,.2f}")
    st.metric("Total Transactions", f"{transactions:,}")
    st.metric("Stores",             f"{stores}")

    st.divider()
    st.caption("Built with Python · FastAPI · SQLite · AWS S3 · Claude AI")


# ── Main tabs ─────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 AI Agent",
    "📦 Products",
    "🏪 Stores",
    "📈 Trends"
])


# ── Tab 1: AI Agent ───────────────────────────────────────────────────────

with tab1:
    st.header("Ask the AI Agent")
    st.caption("Ask any business question — the agent fetches live data and answers automatically")

    # Example questions
    st.write("**Try these:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Top products?"):
            st.session_state.question = "What are the top 5 best selling products?"
    with col2:
        if st.button("Worst store?"):
            st.session_state.question = "Which store is underperforming and why?"
    with col3:
        if st.button("Best category?"):
            st.session_state.question = "Which product category has the best profit margin?"

    # Chat input
    question = st.chat_input("Ask a retail question...")

    if question:
        st.session_state.question = question

    if "question" in st.session_state and st.session_state.question:
        q = st.session_state.question

        with st.chat_message("user"):
            st.write(q)

        with st.chat_message("assistant"):
            if not is_business_question(q):
                st.write("Ask me anything about your retail data — products, stores, revenue, trends!")
            else:
                with st.spinner("Agent thinking..."):
                    answer = run_agent(q)
                st.write(answer)

        # Clear after answering
        st.session_state.question = ""


# ── Tab 2: Products ───────────────────────────────────────────────────────

with tab2:
    st.header("Product Performance")

    df_products = query("""
        SELECT
            p.product_name,
            p.category,
            SUM(f.quantity)               AS units_sold,
            ROUND(SUM(f.sales_amount), 2) AS revenue,
            ROUND(SUM(f.gross_profit), 2) AS profit,
            ROUND(SUM(f.gross_profit) * 100.0
                  / SUM(f.sales_amount), 1) AS margin_pct
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        GROUP BY p.product_name, p.category
        ORDER BY revenue DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_products,
            x="revenue",
            y="product_name",
            orientation="h",
            color="category",
            title="Revenue by Product",
            labels={"revenue": "Revenue (NZD)", "product_name": "Product"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width='stretch')

    with col2:
        fig2 = px.pie(
            df_products,
            values="revenue",
            names="category",
            title="Revenue by Category"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Full Product Table")
    st.dataframe(df_products, use_container_width=True)


# ── Tab 3: Stores ─────────────────────────────────────────────────────────

with tab3:
    st.header("Store Performance")

    df_stores = query("""
        SELECT
            s.city,
            s.region,
            COUNT(f.sale_id)               AS transactions,
            ROUND(SUM(f.sales_amount), 2)  AS revenue,
            ROUND(SUM(f.gross_profit), 2)  AS profit,
            ROUND(AVG(f.sales_amount), 2)  AS avg_sale
        FROM fact_sales f
        JOIN dim_store s ON f.store_id = s.store_id
        GROUP BY s.city, s.region
        ORDER BY revenue DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_stores,
            x="city",
            y="revenue",
            color="region",
            title="Revenue by Store",
            labels={"revenue": "Revenue (NZD)", "city": "Store"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            df_stores,
            x="city",
            y="avg_sale",
            color="region",
            title="Average Transaction Value by Store",
            labels={"avg_sale": "Avg Sale (NZD)", "city": "Store"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Store KPIs")
    st.dataframe(df_stores, use_container_width=True)


# ── Tab 4: Trends ─────────────────────────────────────────────────────────

with tab4:
    st.header("Monthly Revenue Trends")

    df_trend = query("""
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(f.sale_id)               AS transactions,
            ROUND(SUM(f.sales_amount), 2)  AS revenue,
            ROUND(SUM(f.gross_profit), 2)  AS profit
        FROM fact_sales f
        JOIN dim_date d ON f.date = d.date
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    """)

    df_trend["period"] = df_trend["month_name"] + " " + df_trend["year"].astype(str)

    fig = px.line(
        df_trend,
        x="period",
        y=["revenue", "profit"],
        title="Monthly Revenue and Profit",
        labels={"value": "Amount (NZD)", "period": "Month", "variable": "Metric"},
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Best Month",
            df_trend.loc[df_trend["revenue"].idxmax(), "period"],
            f"NZD ${df_trend['revenue'].max():,.2f}"
        )
    with col2:
        st.metric("Lowest Month",
            df_trend.loc[df_trend["revenue"].idxmin(), "period"],
            f"NZD ${df_trend['revenue'].min():,.2f}"
        )

    st.subheader("Monthly Data")
    st.dataframe(df_trend, use_container_width=True)