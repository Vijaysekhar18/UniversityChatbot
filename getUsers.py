import sqlite3

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn
conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT * FROM users")

#cur.execute("DELETE  FROM users")


# Fetch all rows from the cursor
rows = cur.fetchall()
for row in rows:
# Print the fetched rows
  for value in row:
    print(value)