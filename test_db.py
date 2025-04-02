import mysql.connector

try:
    conn = mysql.connector.connect(
        host="sql210.infinityfree.com",
        user="if0_38623850",
        password="SDci3xl8GCsWt",
        database="if0_38623850_budget_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budget_transactions LIMIT 5;")  # Fetch 5 rows
    rows = cursor.fetchall()

    print("✅ Connection Successful! Sample Data:")
    for row in rows:
        print(row)

    conn.close()
except Exception as e:
    print("❌ Connection Failed:", e)
#failed as remote access is not included in free hosting