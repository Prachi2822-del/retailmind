import sqlite3


conn = sqlite3.connect(
    "retailmind.db"
)


cursor = conn.cursor()


cursor.execute(
    "SELECT COUNT(*) FROM sales"
)


result = cursor.fetchone()


print(
    "Sales rows:",
    result[0]
)


conn.close()