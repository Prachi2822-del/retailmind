import pandas as pd

from validator import validate_sales
from loader import load_to_sqlite



print("Starting ETL pipeline")


# Extract
sales = pd.read_csv(
    "data/raw/sales.csv"
)


print(
    f"Loaded {len(sales)} rows"
)


# Transform
clean_sales = validate_sales(
    sales
)


print(
    f"Clean rows: {len(clean_sales)}"
)


# Load
load_to_sqlite(
    clean_sales
)


print(
    "ETL completed successfully"
)