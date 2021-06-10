from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = '98b8703fefdf4d3280133e573271e7b9'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = '****'
app.config['MYSQL_PASSWORD'] = '*******'
app.config['MYSQL_DB'] = 'users'

# Intialize MySQL
mysql = MySQL(app)

def is_logged_in(func):
    @wraps(func)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('You are not logged in, please login','danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM useraccounts WHERE username=%s",(username,))
            account = cursor.fetchone()
            if account and check_password_hash(account['password'], password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                flash("Login failed. Please check e-mail and password", "danger")
        except Exception as e:
                flash("Username is not found", "danger")
    return render_template('index.html', msg='')


@app.route('/register', methods=['GET','POST'])
def register():
    if username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM useraccounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                flash("Account already exists!", "danger")
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash("Invalid email address!", "danger")
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash("Username must contain only characters and numbers!", "danger")
            elif not username or not password or not email:
                flash("Please fill out the form!", "danger")
            else:
                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, generate_password_hash(password), email))
                mysql.connection.commit()
                flash("You have successfully registered!")
        except Exception as e:
            flash("Oops! Something went wrong","danger")
    elif request.method == 'POST':
        flash("Please fill out all the required fields!", "danger")
    return render_template('register.html', msg='')

@app.route('/deactivate/<string:id>', methods=['DELETE'])
@is_logged_in
def deactivate(id):
    """This method is used to deactivate the user"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM useraccounts WHERE id = %s', (id,))
    except Exception as e:
        flash("Something went wrong", "danger")
    flash("We are sad to see you go!")
    return redirect(url_for('home'))

@app.route('/change/<string:id>', methods=['PUT'])
@is_logged_in
def change(id):
    """This method is used to change email/password of a logged in user"""
    password = request.form['password']
    email = request.form['email']

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE useraccounts set password = %s, email = %s WHERE id = %s', (generate_password_hash(password), email, id,))
    except Exception as e:
        flash("Something went wrong", "danger")
    flash("Your profile is updated, Please login again!")
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

if __name__ =='__main__':
	app.run(Debug=True)
