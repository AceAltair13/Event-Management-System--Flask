from flask import Flask, render_template,request,redirect,session,url_for,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yash'
app.config['MYSQL_DB'] = 'flaskapp'

mysql = MySQL(app)


registered_events = [
    {
        'event_name': "Yash's Birthday",
        'event_type': "Birthday",
        'event_location': "Kalyan",
        'organiser': "Yash",
        'date_booked': "2-Feb-2019",
    },
    {
        'event_name': "Throwback Party",
        'event_type': "Party",
        'event_location': "Mumbai",
        'organiser': "Tirth",
        'date_booked': "2-July-2019",
    },
    {
        'event_name': "XYZ's Anniversary",
        'event_type': "Anniversary",
        'event_location': "Ahmedabad",
        'organiser': "XYZ",
        'date_booked': "2-May-2019",
    }


]


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/users/<username>',methods = ['GET','POST'])
def dashboard(username):
    if 'loggedin' in session:
        return render_template('dashboard.html', events=registered_events, name=username)
    return render_template('/login.html')


@app.route('/login',methods = ['GET','POST'])
def login():
        msg = ''
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = MD5(%s)",(username, password))
            account = cursor.fetchone()
            
            if account:
                last_login = datetime.now()
                session['loggedin'] = True
                session['password'] = account['password']
                session['username'] = account['username']
                login_time = datetime.now()
                cursor.execute("UPDATE users SET last_login = %s where username=%s",(last_login,session['username']))
                mysql.connection.commit()
                cursor.close()
                return render_template('dashboard.html')
            else:
                return "<h1>Invalid username or password</h1>"
        return render_template('login.html')


@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        email = userDetails['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            return "<h1>Username already exists</h1>"
        else:
            cursor.execute("INSERT INTO users(username,password,email) VALUES(%s,MD5(%s),%s)",
                    (username,password, email))
            mysql.connection.commit()
            cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/<eventname>')
def event(eventname):
    if eventname == 'birthday':
        return render_template('birthday.html')
    elif eventname == 'anniversary':
        return render_template('anniversary.html')
    elif eventname == 'others':
        return render_template('other_event.html')
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
