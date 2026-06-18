import pandas as pd


def validate_sales(df):

    print("Starting validation...")


    # Check missing values
    missing = df.isnull().sum()

    print("\nMissing values:")
    print(missing)


    # Remove invalid quantity
    invalid_quantity = df[df["quantity"] <= 0]


    print(
        f"\nInvalid quantity rows: {len(invalid_quantity)}"
    )


    # Keep valid rows
    df = df[df["quantity"] > 0]


    return df