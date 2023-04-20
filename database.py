# https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
import sqlite3
import os.path

if not os.path.exists("data/database.db"):

# customer table
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	SQL_STATEMENT = """CREATE TABLE customer (
		cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
		email VARCHAR(50),
		pass VARCHAR(30),
		fname VARCHAR(30),
		lname VARCHAR(30),
		phone VARCHAR(40),
		sign_up TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);"""

	cursor.execute(SQL_STATEMENT)
	conn.commit()
	cursor.close()
	conn.close()

# shipping table
	cursor = None
	conn = None
	
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	SQL_STATEMENT = """CREATE TABLE shipping (
		ship_id INTEGER PRIMARY KEY AUTOINCREMENT,
		address TEXT,
		apt_num VARCHAR(20),
		city VARCHAR(30),
		state CHAR(2),
		zip CHAR(9),
		in_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		cust_id INTEGER NOT NULL,
		FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
	);"""

	cursor.execute(SQL_STATEMENT)
	conn.commit()
	cursor.close()
	conn.close()

# service table 
	cursor = None
	conn = None
	
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()
	
	SQL_STATEMENT = """CREATE TABLE service (
		serv_id INTEGER PRIMARY KEY AUTOINCREMENT,
		dtype VARCHAR(20),
		dbrand VARCHAR(20),
		dmodel VARCHAR(20),
		dserial VARCHAR(20),
		idescript TEXT,
		repair_serv BOOLEAN DEFAULT 0,
		data_serv BOOLEAN DEFAULT 0,
		virus_serv BOOLEAN DEFAULT 0,
		diagn_serv BOOLEAN DEFAULT 0,
		softwr_serv BOOLEAN DEFAULT 0,
		install_serv BOOLEAN DEFAULT 0,
		serv_dt  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		cust_id INTEGER NOT NULL,
		FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
	);"""

	cursor.execute(SQL_STATEMENT)
	conn.commit()
	cursor.close()
	conn.close()

# recycle table
	cursor = None
	conn = None
	
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	SQL_STATEMENT = """CREATE TABLE recycle (
		recyc_id INTEGER PRIMARY KEY AUTOINCREMENT,
		recyc_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		cust_id INTEGER NOT NULL,
		FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
	);"""

	cursor.execute(SQL_STATEMENT)
	conn.commit()
	cursor.close()
	conn.close()

# inventory table
	cursor = None
	conn = None
	
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	# or REAL for decimal
	SQL_STATEMENT = """CREATE TABLE inventory (
		item_id INTEGER PRIMARY KEY AUTOINCREMENT,
		item VARCHAR(50),
		description TEXT,
		category TEXT,
		url VARCHAR(100),
		image TEXT,
		price DECIMAL(10, 2), 
		inventory INTEGER, 
		in_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);"""

	cursor.execute(SQL_STATEMENT)
	conn.commit()
	cursor.close()
	conn.close()

# cart table
	cursor = None
	conn = None
	
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	SQL_STATEMENT = """CREATE TABLE cart (
		cust_id INTEGER NOT NULL,
		item_id INTEGER NOT NULL,
		FOREIGN KEY (cust_id) REFERENCES customer(cust_id),
		FOREIGN KEY (item_id) REFERENCES inventory(item_id)
	);"""

	cursor.execute(SQL_STATEMENT)
	conn.commit()
	cursor.close()
	conn.close()

# order/history table
	cursor = None
	conn = None
	
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	SQL_STATEMENT = """CREATE TABLE orders (
		or_id INTEGER PRIMARY KEY AUTOINCREMENT,
		cust_id INTEGER NOT NULL,
		total DECIMAL(10, 2),
		ship_id INTEGER NOT NULL,
		or_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (cust_id) REFERENCES customer(cust_id),
		FOREIGN KEY (ship_id) REFERENCES shipping(ship_id)
	);"""
	
	cursor.execute(SQL_STATEMENT)
	conn.commit()
	
	# close connection to db
	cursor.close()
	conn.close

# insert mockup data
	cursor = None
	conn = None
	
	# establish connection to database
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()


	cursor.execute("INSERT INTO customer (email, pass, fname, lname, phone) VALUES \
		('john.doe@example.com', 'password1', 'John', 'Doe', '123-456-7890'), \
		('jane.doe@example.com', 'password2', 'Jane', 'Doe', '098-765-4321'), \
		('leo@email.com', 'test', 'Leo', 'Benitez', '098-765-4321'), \
		('jim.smith@example.com', 'password3', 'Jim', 'Smith', '555-555-5555');")
    
	conn.commit()
	conn.close()

	cursor = None
	conn = None

	# establish connection to database
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()


	cursor.execute("INSERT INTO shipping (address, apt_num, city, state, zip, cust_id) VALUES \
		('address1', 'apt1', 'atl', 'ga', '17890', '1'), \
		('address2', 'apt2', 'atl', 'ga', '17890', '2'), \
		('address3', 'apt3', 'atl', 'ga', '17890', '3'), \
		('address4', 'apt4', 'atl', 'ga', '17890', '4');")
    
	conn.commit()
	conn.close()

	cursor = None
	conn = None
	
	# establish connection to database
	conn = sqlite3.connect("data/database.db")
	cursor = conn.cursor()

	# insert mockup data into inventory table
	cursor.execute("""
    	INSERT INTO inventory (item, description, category, url, image, price, inventory)
    	VALUES 
        	("Product A", "This is the description for Product A", "Category A", "https://example.com/product-a", "image_a.jpg", 9.99, 10),
        	("Product B", "This is the description for Product B", "Category B", "https://example.com/product-b", "image_b.jpg", 19.99, 20),
        	("Product C", "This is the description for Product C", "Category A", "https://example.com/product-c", "image_c.jpg", 29.99, 30)
		""")

	# commit changes and close connection
	conn.commit()
	cursor.close()
	conn.close()

else:
	conn = sqlite3.connect("data/database.db")
	conn.close()








