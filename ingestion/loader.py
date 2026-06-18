import sqlite3


def load_to_sqlite(df):

    conn = sqlite3.connect(
        "retailmind.db"
    )


    df.to_sql(
        "sales",
        conn,
        if_exists="replace",
        index=False
    )


    conn.close()


    print("Data loaded into SQLite")