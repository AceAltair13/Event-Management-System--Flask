from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'acbdsabfasbfk1j3b431123jb21321kk3k4ob'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'project'

mysql = MySQL(app)

# TIMESTAMPDIFF(YEAR, dob, CURDATE()) AS age;

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
    },
]

# Pricing formula: max_people*pricing[tier n]['person_cost'] + pricing['tier n']['base']

pricing = {
    'tier 1': {
        'base': 15000,
        'person': 1500
    },
    'tier 2': {
        'base': 30000,
        'person': 3750,
    },
    'tier 3': {
        'base': 75000,
        'person': 7500,
    },
    'tier 4': {
        'base': 150000,
        'person': 10500
    },
}

@app.route('/')
@app.route('/home')
def index():
    if 'loggedin' in session:
        return render_template('index.html', session=session['loggedin'], name=session['username'])
    else:
        return render_template('index.html', session=False)


@app.route('/users/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'loggedin' in session and username == session['username']:
        return render_template('dashboard.html', events=registered_events, name=username)
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = MD5(%s)", (username, password)
        )
        account = cursor.fetchone()

        if account:
            last_login = datetime.now()
            session['loggedin'] = True
            session['username'] = account['username']
            session['password'] = account['password']
            cursor.execute(
                "UPDATE users SET last_login = %s where username=%s",
                (last_login, session['username']),
            )
            mysql.connection.commit()
            cursor.close()
            return render_template(
                'index.html',
                session=session['loggedin'],
                name=session['username'],
                msg="Login Successful!",
            )
        else:
            return render_template("login.html", msg="Invalid Username or Password!")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    rmsg = ""
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        email = userDetails['email']
        repass = userDetails['reenterPassword']
        if password != repass:
            rmsg = "Password does not match!"
            return render_template("register.html", rmsg=rmsg)
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s", [username])
            account = cursor.fetchone()

            if account:
                rmsg = "Username already exists!"
                return render_template("register.html", rmsg=rmsg)
            else:
                cursor.execute(
                    "INSERT INTO users(username,password,email) VALUES(%s,MD5(%s),%s)",
                    (username, password, email),
                )
                mysql.connection.commit()
                cursor.close()
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('index'))


@app.route('/<eventname>', methods=['GET', 'POST'])
def book_event(eventname: str):
    try:
        if 'loggedin' in session:
            return render_template(
                'booking.html',
                session=session['loggedin'],
                name=session['username'],
                event=eventname.capitalize(),
            )
        else:
            return render_template('login.html')
    except KeyError:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
