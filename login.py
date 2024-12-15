from flask import Flask, request, render_template, redirect, session
import os
import sqlite3

currentlocation = os.path.dirname(os.path.abspath(__file__))

myapp = Flask(__name__)
myapp.secret_key = 'your_secret_key_here'  # Secret key for session management

# Initialize the database
def init_db():
    sqlconnection = sqlite3.connect(currentlocation + '/login.db')
    cursor = sqlconnection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        Username TEXT PRIMARY KEY, 
        Password TEXT NOT NULL
    )''')
    sqlconnection.commit()
    sqlconnection.close()

@myapp.route('/')
def homepage():
    if 'username' in session:
        return redirect('/index')  # Redirect to the chat page if already logged in
    return render_template('loggedin.html')

@myapp.route('/', methods=['POST'])
def login():
    UN = request.form['Username']
    PW = request.form['Password']

    # Connect to the database
    sqlconnection = sqlite3.connect(currentlocation + '/login.db')
    cursor = sqlconnection.cursor()

    # Use parameterized query to prevent SQL injection
    query = "SELECT Username, Password FROM Users WHERE Username = ? AND Password = ?"
    cursor.execute(query, (UN, PW))
    rows = cursor.fetchall()

    sqlconnection.close()

    if len(rows) == 1:
        session['username'] = UN  # Store username in the session
        return redirect('/index')
    else:
        return redirect('/register')

@myapp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        dUN = request.form['DUsername']
        dPW = request.form['DPassword']

        # Connect to the database
        sqlconnection = sqlite3.connect(currentlocation + '/login.db')
        cursor = sqlconnection.cursor()

        # Check if the username already exists
        query = "SELECT Username FROM Users WHERE Username = ?"
        cursor.execute(query, (dUN,))
        existing_user = cursor.fetchone()

        if existing_user:
            sqlconnection.close()
            return "Username already exists. Please choose another one."

        # Use parameterized query to insert user
        query = "INSERT INTO Users (Username, Password) VALUES (?, ?)"
        cursor.execute(query, (dUN, dPW))
        sqlconnection.commit()
        sqlconnection.close()

        return redirect('/')
    return render_template('register.html')

@myapp.route('/index')
def index():
    if 'username' not in session:
        return redirect('/')  # Redirect to login if not logged in
    return render_template('index.html', username=session['username'])

@myapp.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect('/')  # Redirect to login page

if __name__ == '__main__':
    init_db()  # Ensure the database and table are initialized
    myapp.run(debug=True)
