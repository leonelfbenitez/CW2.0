from flask import *
import sqlite3

# function to parse retrieved database data
def parse(data):

    ans = [] # initiate array to store total records 
    i = 0 # initiate iteration

    # iterate the number of rows in data
    while i < len(data):

        curr = [] # set array to store values per record
        
        # iterate the number of columns
        for j in range(8):

            # if row iteration is over limit
            if i >= len(data):
                break

            # else, append new value to record
            curr.append(data[i])
            i += 1
        
        # append record to total records
        ans.append(curr)
    
    # return total records
    return ans

# open connection to db
conn = sqlite3.connect("data/database.db")
cursor = conn.cursor()

category = "Category A"

# get available inventory for selected category
cursor.execute('SELECT item_id, item, description, category, image, price, inventory FROM inventory WHERE category = ?;', (category, ))
results = cursor.fetchall()
        
# close connection to db
cursor.close()
conn.close()

# get list of categories
categoryNames = results[0][3]

# print the list of tuples
print(categoryNames)

