# test-vuln.py
import sqlite3

def get_user(user_id):
    admin_password = "SuperSecret123!"
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()
