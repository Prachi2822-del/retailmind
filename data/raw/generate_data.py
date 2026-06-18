import pandas as pd
import random
from pathlib import Path

# Create data folder
Path("data/raw").mkdir(parents=True, exist_ok=True)

# Products
products = pd.DataFrame({
    "product_id": range(1, 11),
    "product_name": [
        "Laptop", "Mouse", "Keyboard", "Monitor", "Printer",
        "Headphones", "Tablet", "Camera", "Speaker", "Phone"
    ],
    "price": [1200, 25, 60, 350, 180, 90, 500, 700, 150, 1000]
})

# Stores
stores = pd.DataFrame({
    "store_id": [1, 2, 3],
    "store_name": ["Sydney", "Melbourne", "Brisbane"]
})

# Customers
customers = pd.DataFrame({
    "customer_id": range(1, 101),
    "customer_name": [f"Customer_{i}" for i in range(1, 101)]
})

# Sales
sales_rows = []

for sale_id in range(1, 5001):
    product_id = random.randint(1, 10)
    quantity = random.randint(1, 5)

    sales_rows.append({
        "sale_id": sale_id,
        "product_id": product_id,
        "store_id": random.randint(1, 3),
        "customer_id": random.randint(1, 100),
        "quantity": quantity
    })

sales = pd.DataFrame(sales_rows)

# Save CSV files
products.to_csv("data/raw/products.csv", index=False)
stores.to_csv("data/raw/stores.csv", index=False)
customers.to_csv("data/raw/customers.csv", index=False)
sales.to_csv("data/raw/sales.csv", index=False)

print("Generated 5,000 sales rows")