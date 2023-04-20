from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import logging


# flask app initiated
app = Flask(__name__)

# secret key for flask login session
app.secret_key = "secret_key_101"

# inventory information
INV_FOLDER = "static/inventory"
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['INV_FOLDER'] = INV_FOLDER

# function check valid inventory pic
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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


# function to retrieve customer's login status
def getLoginDetails():
    try:
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()

        # if customer not logged in:
        if not session:
            fname = ""
            lname = ""
            noOfItems = 0
            loggedIn = False
        
        # else, customer is already logged in:
        else:

            # from session, get customer's info
            cursor.execute("SELECT cust_id, fname, lname FROM customer WHERE email = ?;", (session['email'], ))
            cust_id, fname, lname = cursor.fetchone()

            # from session, get cart info
            cursor.execute("SELECT COUNT(item_id) FROM cart WHERE cust_id = ?;", (cust_id, ))
            noOfItems = cursor.fetchone()[0]

            loggedIn = True
            
        # close connection to db
        cursor.close()
        conn.close()

        # return data to caller
        return (loggedIn, fname, lname, noOfItems)

    # if any errors/exceptions:
    except Exception as e:

        # close connection to db
        cursor.close()
        conn.close()

        msg = {
            'status': 500,
            'message': 'Error: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# function to verify login is valid:
def is_valid(email, password):

    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # retrieve email and password from customer table
        cursor.execute('SELECT email, pass FROM customer WHERE email = ?;', (session['email'], ))
        data = cursor.fetchone()

        # close connection to db
        cursor.close()
        conn.close()

        # for retrieved results
        for row in data:

            # compare email and password given match values in customer table
            if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
                
                # if match found, return true
                return True
        
        # no match found
        return False

    # if any errors/exceptions
    except Exception as e:
        
        msg = {
            'status': 500,
            'message': 'Error 2: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# home/index route
@app.route("/")
def root():
    try:
        # get custome'r login session status
        # loggedIn, fname, lname, noOfItems = getLoginDetails()
        fname = ''
        lname = ''
        noOfItems = 0
        loggedIn = False

        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # get inventory information to display
        cursor.execute('SELECT item_id, item, description, category, url, image, price, inventory FROM inventory;')
        itemData = cursor.fetchall()
        data = parse(itemData)

        # get category information to display
        cursor.execute('SELECT DISTINCT category FROM inventory;')
        catData = cursor.fetchall()

        # create a list of category names by iterating over the tuples and extracting the first element
        categoryData = [category[0] for category in catData]

        # create a list of tuples with IDs starting from 0
        categories = list(enumerate(categoryData))

        # close connection to db
        cursor.close()
        conn.close()

        # return data to frontend
        return render_template('home.html', loggedIn=loggedIn, itemData=data, categoryData=categories, firstName=fname, lastName=lname, noOfItems=noOfItems)

    # if any errors/exceptions
    except Exception as e:  
        msg = {
            'status': 500,
            'message': 'Error 3: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# get categories for add to inventory route:
@app.route("/add")
def admin():

    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # get categories for all items
        cursor.execute('SELECT DISTINCT category FROM inventory;')
        categories = cursor.fetchall()

        # close connection to db
        cursor.close()
        conn.close()

        # return data to frontend
        return render_template('add.html', categories=categories)

    # if any errors/exceptions
    except Exception as e:
        
        # close connection to db
        cursor.close()    
        conn.close()
        
        msg = {
            'status': 500,
            'message': 'Error 4: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# add inventory items from form route
@app.route("/addItem", methods=["GET", "POST"])
def addItem():

    # POST data retrieved from HTML form
    if request.method == "POST":
        item = request.form['item']
        description = request.form['description']
        category = int(request.form['category'])
        price = float(request.form['price'])
        inventory = int(request.form['inventory'])
    

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = filename
        
        try:
            # open connection to db
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()

            # insert item data into table
            cursor.execute('''INSERT INTO products (item, description, category, image, price, inventory) 
                        VALUES (?, ?, ?, ?, ?, ?);''', (item, description, category, image, price, inventory))
            conn.commit()

            # close connection to db
            cursor.close()
            conn.close()

            # return OK
            msg = {
                'status': 200,
                'message': 'OK'
            }
            resp = jsonify(msg)
            resp.status_code = 200
            return resp

        # if any errors/exceptions
        except Exception as e:
            
            # close connection to db
            cursor.close()    
            conn.close()
            
            msg = {
                'status': 500,
                'message': 'Error 5: ' + str(e)
            }
            resp = jsonify(msg)
            resp.status_code = 500
            return resp


# get inventory data for removal route
@app.route("/remove")
def remove():

    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # get data for all items in inventory
        cursor.execute('SELECT item_id, item, description, category, image, price, inventory FROM inventory;')
        results = cursor.fetchall()

        # close connection to db
        cursor.close()
        conn.close()

        # return data
        return render_template('remove.html', data=results)

    # if any errors/exceptions
    except Exception as e:
        
        # close connection to db
        cursor.close()    
        conn.close()
        
        msg = {
            'status': 500,
            'message': 'Error 6: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# remove item from inventory route
@app.route("/removeItem")
def removeItem():

    try:
        # get item to delete from frontend
        item_id = request.args.get('item_id')

        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # delete given item from db
        cursor.execute('DELETE FROM inventory WHERE item_id = ?;', (item_id, ))
        conn.commit()

        # close connection to db
        cursor.close()
        conn.close()

        # return user to main page
        return redirect(url_for('root'))

    # if any errors/exceptions
    except Exception as e:
        
        # close connection to db
        cursor.close()    
        conn.close()
        
        msg = {
            'status': 500,
            'message': 'Error 7: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# display categories for home 
@app.route("/displayCategory")
def displayCategory():
    
    try:        
        # get customer's login status
        loggedIn, fname, lname, noOfItems = getLoginDetails()

        # get selected category from frontend
        category = request.args.get("category")

        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # get available inventory for selected category
        cursor.execute('SELECT item_id, item, description, category, image, price, inventory FROM inventory WHERE category = ?;', (category, ))
        results = cursor.fetchall()
        
        # close connection to db
        cursor.close()
        conn.close()

        # get list of categories
        categoryNames = results[0][1]
        data = parse(results)

        # forward categories to frontend
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=fname, lastName=lname, noOfItems=noOfItems, categoryName=categoryNames)
    
    # if any errors/exceptions
    except Exception as e:
        
        msg = {
            'status': 500,
            'message': 'Error 8: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# get info for customer's profile route
@app.route("/account/profile")
def profileHome():

    # if customer is not logged in; not found in current session
    if 'email' not in session:

        # redirect customer to login 
        return redirect(url_for('root'))
    
    # else, customer is already logged in:
    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # get customer's info
        cursor.execute("SELECT email, phone, sign_up FROM customer WHERE email = ?;", (session['email'], ))
        results = cursor.fetchall()

        # get custome'r login session status
        loggedIn, fname, lname, noOfItems = getLoginDetails()

        # close connection to db
        cursor.close()    
        conn.close()

        # return info to frontend
        return render_template("profileHome.html", loggedIn=loggedIn, firstName=fname, lastName=lname, noOfItems=noOfItems, data=results)

    # if any errors/exceptions
    except Exception as e:

        # close connection to db
        cursor.close()    
        conn.close()
        
        msg = {
            'status': 500,
            'message': 'Error 9: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# view customer's info route
@app.route("/account/profile/view")
def viewProfile():

    # if customer not logged in; not found in current session
    if 'email' not in session:

        # redirect cutomer to home page
        return redirect(url_for('root'))
    
    # else customer is already logged in:

    # get customer's login status
    loggedIn, fname, lname, noOfItems = getLoginDetails()
    
    
    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # get current customer's info
        cursor.execute("SELECT c.cust_id, c.email, c.fname, c.lname, c.phone, c.sign_up, s.address, s.state, s.zip, s.apt_num FROM customer c, shipping s WHERE c.cust_id = s.cust_id AND c.email = ?", (session['email'], ))
        results = cursor.fetchone()
        
        # close connection to db
        cursor.close()
        conn.close()

        # return info to frontend
        return render_template("viewProfile.html", data=results, loggedIn=loggedIn, firstName=fname, lastName=lname, noOfItems=noOfItems)

    # if any errors/exceptions
    except Exception as e:

        # close connection to db
        cursor.close()    
        conn.close()

        msg = {
            'status': 500,
            'message': 'Error 10: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# edit customer's info route
@app.route("/account/profile/edit")
def editProfile():

    # if customer not logged in; not found in current session
    if 'email' not in session:

        # redirect cutomer to home page
        return redirect(url_for('root'))
    
    # else customer is already logged in:

    # get customer's login status
    loggedIn, fname, lname, noOfItems = getLoginDetails()
    
    
    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # get customer's info
        cursor.execute("SELECT cust_id, email, fname, lname, phone, sign_up FROM customer WHERE email = ?;", (session['email'], ))
        customerInfo = cursor.fetchone()

        cust_id = customerInfo[0]
 
        # get customer's shipping info
        cursor.execute("SELECT address, apt_num, city, state, zip FROM shipping WHERE cust_id = ?;", (cust_id, ))
        shippingInfo = cursor.fetchone()

        # close connection to db
        cursor.close()
        conn.close()

        # return info to frontend
        return render_template("editProfile.html", cust_info=customerInfo, ship_info=shippingInfo, loggedIn=loggedIn, firstName=fname, lastName=lname, noOfItems=noOfItems)

    # if any errors/exceptions
    except Exception as e:

        # close connection to db
        cursor.close()    
        conn.close()

        msg = {
            'status': 500,
            'message': 'Error 10: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
        return resp


# change password route 
@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():

    # if customer is not logged in; not found in current session
    if 'email' not in session:

        # redirect customer to login 
        return redirect(url_for('loginForm'))
    
    # POST data retrieved from frontend; encript passwords
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
    
        try:
            # open connection to db
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # get customer's current password
            cursor.execute("SELECT cust_id, password FROM users WHERE email = ?", session['email'])
            cust_id, passw = cursor.fetchone()
            
            # verify current password is not the same as new password:
            if (passw == oldPassword):
                
                try:
                    # set new password in customer table
                    cursor.execute("UPDATE customer SET pass = ? WHERE cust_id = ?", newPassword, cust_id)
                    conn.commit()
                    
                    # close connection to db
                    cursor.close()
                    conn.close()

                    # return OK
                    msg = {
                        'status': 200,
                        'message': 'OK'
                    }
                    resp = jsonify(msg)
                    resp.status_code = 200

                # if error in db update:
                except Exception as e:
                    conn.rollback()

                    # close connection to db
                    cursor.close()
                    conn.close()

                    # return error
                    msg = {
                        'status': 507,
                        'message': 'Database update error! ' + str(e)
                    }                    
                    resp = jsonify(msg)
                    resp.status_code = 507

                # return resp to frontend
                return render_template("changePassword.html", msg=resp)
            
            # else, newPassword = oldPassword:
            else:
                msg = {
                    'status': 402,
                    'message': "Same passwords!"
                }
                resp = jsonify(msg)

            # close connection to db
            cursor.close()    
            conn.close()

            # return resp to frontend
            return render_template("changePassword.html", msg=resp)
        
        # if any errors/exceptions:
        except Exception as e:
            # close connection to db
            cursor.close()    
            conn.close()

            msg = {
                'status': 500,
                'message': 'Error 11: ' + str(e)
            }
            resp = jsonify(msg)
            resp.status_code = 500
            return resp

    # else this is just rendering the page
    else:
            return render_template("changePassword.html")


# update profile information route
@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():

    # POST information retrieved from frontend
    if request.method == 'POST':
        fname = request.form['firstName']
        lname = request.form['lastName']
        phone = request.form['phone']
        address = request.form['address']
        apt_num = request.form['apt_num']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']

        try: 
            # open connection to db
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()

            # update customer table with POST values
            cursor.execute("UPDATE customer SET fname = ?, lname = ?, phone = ? WHERE email = ?", (fname, lname, phone, session['email']))
            conn.commit()

            cursor.close()
            conn.close()

            cursor = None
            conn = None

            # open connection to db
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()

            # get cust_id from customer table
            cursor.execute("SELECT cust_id FROM customer WHERE email = ?;", (session['email'], ))
            customerInfo = cursor.fetchone()
            cust_id = customerInfo[0]

            # update shipping table with POST values
            cursor.execute("UPDATE shipping SET address = ?, apt_num = ?, city = ?, state = ?, zip = ? WHERE cust_id = ?;", (address, apt_num, city, state, zip, cust_id))
            conn.commit()

            cursor.close()
            conn.close()

            # return OK
            msg = {
                'status': 200,
                'message': 'OK'
            }
            resp = jsonify(msg)
            resp.status_code = 200        

        # if any errors/exceptions:
        except Exception as e:
            
            conn.rollback()

            # close connection to db
            cursor.close()
            conn.close()

            msg = {
                'status': 500,
                'message': 'Error 12: ' + str(e)
            }
            resp = jsonify(msg)
            resp.status_code = 500
            return resp

    # else just render page
    return redirect(url_for('editProfile'))


# login form route
@app.route("/loginForm")
def loginForm():
    
    # if customer is logged in:
    if 'email' in session:

        # redirect customer to home page
        return redirect(url_for('root'))
    
    # else redirect customer to login page
    else:
        return render_template('login.html', error='')


# login page route
@app.route("/login", methods = ['POST', 'GET'])
def login():

    # POST info is retrieved from frontend
    if request.method == 'POST':
        email = request.form['email']
        passw = request.form['password']

        # verify values are not Null:
        if is_valid(email, passw):

            # reset the current session
            session['email'] = email

            # redirect 
            return redirect(url_for('root'))
        
        # else, email/password mismatch
        else:
            error = 'Invalid Email / Password'
            return render_template('login.html', error=error)


# inventory item information route
@app.route("/itemInformation")
def itemInformation():

    # get customer login status
    loggedIn, fname, lname, noOfItems = getLoginDetails()

    # get the item_id selected from frontend url request
    item_id = request.args.get('item_id')


    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # retrieve information from inventory table
        cursor.execute('SELECT item_id, item, description, category, url, image, price, inventory FROM inventory WHERE item_id = ?', item_id)
        
        # retrieve the record found
        item_data = cursor.fetchone()
        
        # close connection to db
        cursor.close()
        conn.close()

    # if any errors/exceptions:
    except Exception as e:

        # close connection to db
        cursor.close()
        conn.close()

        msg = {
            'status': 500,
            'message': 'Error 13: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
    
    # return information to the frontend 
    return render_template("productDescription.html", data=item_data, loggedIn = loggedIn, firstName = fname, lastName = lname, noOfItems = noOfItems)


# add item to cart route
@app.route("/addToCart")
def addToCart():

    # if customer is not logged in:
    if 'email' not in session:

        # redirect customer to login form
        return redirect(url_for('loginForm'))
    
    # else, customer is already logged in:
    else:

        # get selected item info from frontend
        item_id = int(request.args.get('item_id'))
        try: 
            # open connection to db
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # get customer's cust_id
            cursor.execute("SELECT cust_id FROM customer WHERE email = ?", (session['email'], ))
            
            # retrieve result row
            cust_id = cursor.fetchone()[0]

            # update cart table
            cursor.execute("INSERT INTO cart (cust_id, item_id) VALUES (?, ?)", (cust_id, item_id))
            conn.commit()

                
            # close connection to db
            cursor.close()
            conn.close()
                
            # return OK
            msg = {
                'status': 200,
                'message': 'OK'
            }
            resp = jsonify(msg)
            resp.status_code = 200   
            
        # if any errors/exceptions:
        except Exception as e:
            
            conn.rollback()

            # close connection to db
            cursor.close()
            conn.close()

            msg = {
                'status': 500,
                'message': 'Error 14: ' + str(e)
            }
            resp = jsonify(msg)
            resp.status_code = 500

    # redirect customer back to home page
    return redirect(url_for('root'))


# get cart info route
@app.route("/cart")
def cart():

    # if customer is not logged in:
    if 'email' not in session:

        # redirect customer to login form
        return redirect(url_for('loginForm'))
    
    # else customer is already logged in:
    # get customer login status
    loggedIn, fname, lname, noOfItems = getLoginDetails()
    
    # get current customer's session email; login info
    email = session['email']
    items = 0
    totalPrice = 0
    
    try:
        # open connection to db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # get cust_id from customer table with session email
        cursor.execute("SELECT cust_id FROM customer WHERE email = ?", (email, ))
        
        # retrieve found record
        cust_id = cursor.fetchone()[0]

        # get item info that are in the cart table
        cursor.execute("SELECT i.item_id, i.item, i.price, i.image FROM inventory i, cart c WHERE i.item_id = c.item_id AND c.cust_id = ?", (cust_id, ))
        items = cursor.fetchall()

        # close connection to db
        cursor.close()
        conn.close()

        # total process:    
        totalPrice = 0
        for row in items:
            totalPrice += row[2]

    # if any errors/exceptions:
    except Exception as e:

        # close connection to db
        cursor.close()
        conn.close()

        msg = {
            'status': 500,
            'message': 'Error 15: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500
    
    # return item info and total to frontend
    return render_template("cart.html", products = items, totalPrice=totalPrice, loggedIn=loggedIn, firstName=fname, lastName=lname, noOfItems=noOfItems)


# remove items from cart route
@app.route("/removeFromCart")
def removeFromCart():

    # if customer is not logged in:
    if 'email' not in session:

        # redirect customer to login form
        return redirect(url_for('loginForm'))
    
    # else customer is already logged in:
    # get current customer's session email
    email = session['email']

    # get selected item
    item_id = int(request.args.get('item_id'))

    try:
        # connect to the db
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # retrieve cust_id from customer table
        cursor.execute("SELECT cust_id FROM customer WHERE email = ?", (email, ))
        cust_id = cursor.fetchone()[0]
        
        # delete item/record from cart
        cursor.execute("DELETE FROM cart WHERE cust_id = ? AND item_id = ?", (cust_id, item_id, ))
        conn.commit()
        
        # OK
        msg = {
            'status': 200,
            'message': 'OK'
        }
        resp = jsonify(msg)
        resp.status_code = 200   
    
    # if any errors/exceptions:
    except Exception as e:

        # close connection to db
        cursor.close()
        conn.close()

        msg = {
            'status': 500,
            'message': 'Error 16: ' + str(e)
        }
        resp = jsonify(msg)
        resp.status_code = 500

    # redirect customer back to home page    
    return redirect(url_for('root'))


# logout route
@app.route("/logout")
def logout():

    # remove customer's email from current session
    session.pop('email', None)

    # redirect customer back to home page
    return redirect(url_for('root'))

# render registration form, route
@app.route("/registerationForm")
def registrationForm():

    # render registration form
    return render_template("register.html")


# POST register data after submit from registrationForm, route
@app.route("/register", methods = ['GET', 'POST'])
def register():

    # POST values retrieved from frontend at submit in registrationForm
    if request.method == 'POST':
        email = request.form['email']    
        passw = request.form['password']
        fname = request.form['firstName']
        lname = request.form['lastName']
        phone = request.form['phone']
        address = request.form['address']
        apt_num = request.form['apt_num']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']

        try:
            # open connection to db
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # insert info int customer table
            cursor.execute('INSERT INTO customer (email, pass, fname, lname, phone) VALUES (?, ?, ?, ?, ?)', email, hashlib.md5(passw.encode()).hexdigest(), fname, lname, phone)
            conn.commit()

            # insert info into shipping table
            cursor.execute('INSERT INTO shipping (address, apt_num, city, state, zip) VALUES (?, ?, ?, ?, ?)', address, apt_num, city, state, zip)
            conn.commit()

            # OK
            msg = {
                'status': 200,
                'message': 'OK'
            }
            resp = jsonify(msg)
            resp.status_code = 200 

        # if any errors/exceptions:
        except Exception as e:
            
            conn.rollback()

            # close connection to db
            cursor.close()
            conn.close()

            msg = {
                'status': 500,
                'message': 'Error 17: ' + str(e)
            }
            resp = jsonify(msg)
            resp.status_code = 500

    # return resp/result to frontend and route customer to login
    return render_template("login.html", msg=resp)


# run flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='3000', debug=True) 
