import sqlite3


# open connection to db
conn = sqlite3.connect("data/database.db")
cursor = conn.cursor()

# get cust_id from customer table
cursor.execute("SELECT cust_id FROM customer WHERE email = ?;", ('leo@email.com', ))
customerInfo = cursor.fetchone()
cust_id = customerInfo[0]
print(cust_id)

# update shipping table with POST values
cursor.execute("UPDATE shipping SET address = ?, apt_num = ?, city = ?, state = ?, zip = ? WHERE cust_id = ?;", ('addressA', 'apt_numA', 'atl', 'ga', '333', cust_id))
conn.commit()

cursor.execute("SELECT * FROM shipping;")
data = cursor.fetchall()

print(data)

# close connection to db
cursor.close()
conn.close()


