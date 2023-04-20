from flask import *
import sqlite3

# open connection to db
conn = sqlite3.connect("data/database.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM customer;")
rows = cursor.fetchall()

for row in rows:
    print(row)

# close connection to db
cursor.close()
conn.close()
