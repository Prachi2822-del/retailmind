import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

PRODUCTS = [
    ("P001", "Whole Milk 2L",         "Dairy",   1.20, 1.89), 
    ("P002", "White Bread 700g",      "Bakery",  0.90, 1.49),
    ("P003", "Free Range Eggs 12pk",  "Dairy",   3.50, 5.99),
    ("P004", "Chicken Breast 1kg",    "Meat",    6.00, 9.99),
    ("P005", "Extra Virgin Olive Oil","Pantry",  4.20, 6.99),
    ("P006", "Cheddar Cheese 500g",   "Dairy",   4.80, 7.49),
    ("P007", "Sourdough Loaf",        "Bakery",  3.20, 5.49),
    ("P008", "Salmon Fillet 400g",    "Seafood", 9.50, 14.99),
    ("P009", "Greek Yoghurt 1kg",     "Dairy",   5.10, 7.99),
    ("P010", "Pasta 500g",            "Pantry",  1.60, 2.79),
]

STORES = [
    ("S01", "Auckland CBD",   "North Island", 1200),
    ("S02", "Wellington",     "North Island",  980),
    ("S03", "Christchurch",   "South Island", 1100),
    ("S04", "Hamilton",       "North Island",  750),
    ("S05", "Tauranga",       "North Island",  860),
]

CUSTOMERS = [
    ("C001", "Alice Johnson", "alice@email.com", "Auckland"),
    ("C002", "Ben Smith",     "ben@email.com",   "Wellington"),
    ("C003", "Carol White",   "carol@email.com", "Christchurch"),
    ("C004", "David Lee",     "david@email.com", "Hamilton"),
    ("C005", "Emma Brown",    "emma@email.com",  "Tauranga"),
]

# ── Sales: 5,000 rows with ~3% intentional bad data ──────────────────
sales_rows = []
start = datetime(2025, 1, 1)

for _ in range(5000):
    product  = random.choice(PRODUCTS)
    store    = random.choice(STORES)
    customer = random.choice(CUSTOMERS)
    date     = start + timedelta(days=random.randint(0, 180))
    qty      = random.randint(1, 20)

    # Inject ~2% null amounts  (validation must catch this)
    amount = round(qty * product[4], 2) if random.random() > 0.02 else None
    # Inject ~1% negative quantities  (validation must catch this)
    quantity = qty if random.random() > 0.01 else -qty

    sales_rows.append({
        "sale_id":      str(uuid.uuid4()),
        "date":         date.strftime("%Y-%m-%d"),
        "store_id":     store[0],
        "product_id":   product[0],
        "customer_id":  customer[0],
        "quantity":     quantity,
        "sales_amount": amount,
    })

# ── Reference tables ─────────────────────────────────────────────────
product_rows = [
    {"product_id": p[0], "name": p[1],
     "category": p[2], "cost_price": p[3], "sell_price": p[4], "is_active": True}
    for p in PRODUCTS
]

store_rows = [
    {"store_id": s[0], "city": s[1],
     "region": s[2], "size_sqm": s[3]}
    for s in STORES
]

customer_rows = [
    {"customer_id": c[0], "name": c[1],
     "email": c[2], "city": c[3]}
    for c in CUSTOMERS
]

# ── Save to data/raw/ ────────────────────────────────────────────────
pd.DataFrame(sales_rows).to_csv("data/raw/sales.csv",      index=False)
pd.DataFrame(product_rows).to_csv("data/raw/products.csv", index=False)
pd.DataFrame(store_rows).to_csv("data/raw/stores.csv",     index=False)
pd.DataFrame(customer_rows).to_csv("data/raw/customers.csv", index=False)

print(f"Generated {len(sales_rows):,} sales rows")
print(f"Generated {len(product_rows)} products")
print(f"Generated {len(store_rows)} stores")
print(f"Generated {len(customer_rows)} customers")
print("Saved to data/raw/")