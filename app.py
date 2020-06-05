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
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# TIMESTAMPDIFF(YEAR, dob, CURDATE()) AS age;

events_available = ['birthday', 'anniversary', 'other']

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

# Pricing formula: max_people*pricing[tier n]['person'] + pricing['tier n']['base']

pricing = {
    'birthday': {
        'tier 1': {'base': 7500, 'person': 750},
        'tier 2': {'base': 10000, 'person': 1000},
        'tier 3': {'base': 12500, 'person': 1250},
        'tier 4': {'base': 17000, 'person': 1550},
    },
    'anniversary': {
        'tier 1': {'base': 9000, 'person': 1000},
        'tier 2': {'base': 12000, 'person': 1300},
        'tier 3': {'base': 15000, 'person': 1600},
        'tier 4': {'base': 20000, 'person': 1900},
    },
    'other': {
        'tier 1': {'base': 8000, 'person': 875},
        'tier 2': {'base': 11000, 'person': 1150},
        'tier 3': {'base': 14000, 'person': 1400},
        'tier 4': {'base': 18500, 'person': 1700},
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
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT p.*, TIMESTAMPDIFF(YEAR, dob, CURDATE()) AS age, c.*
            from personal p NATURAL JOIN contact c WHERE pid =
            (SELECT pid from has WHERE uid =
            ( SELECT uid from users WHERE username = %s)) 
            '''
            ,[session['username']]
        )
        personal_details = cursor.fetchone()
        cursor.execute('''
            SELECT COUNT(eid) as count FROM books WHERE uid = 
            (SELECT uid FROM users WHERE username = %s)
            ''', [session['username']]
        )
        count_event = cursor.fetchone()
        cursor.execute('''
            SELECT e.*, b.* FROM event e NATURAL JOIN books b WHERE eid =
            (SELECT eid FROM books WHERE uid = 
            (SELECT uid FROM users WHERE username = %s ))
            ''', [session['username']]
        )
        event_details = cursor.fetchall()
        # return '<h1>' + str(personal_details) + '</h1>'
        return render_template(
            'dashboard.html',
            name=username,
            pdata=personal_details,
            cn=count_event,
            events=event_details
            )
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
    if eventname in events_available:
        if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT pid FROM has WHERE uid = (SELECT uid from users where username = %s)",
                [session['username']],
            )
            per_details = cursor.fetchone()
            if not per_details:
                return redirect(url_for('personal'))
            return render_template(
                'booking.html',
                session=session['loggedin'],
                name=session['username'],
                event=eventname.capitalize(),
                t1_base=pricing[eventname]['tier 1']['base'],
                t2_base=pricing[eventname]['tier 2']['base'],
                t3_base=pricing[eventname]['tier 3']['base'],
                t4_base=pricing[eventname]['tier 4']['base'],
                t1_per=pricing[eventname]['tier 1']['person'],
                t2_per=pricing[eventname]['tier 2']['person'],
                t3_per=pricing[eventname]['tier 3']['person'],
                t4_per=pricing[eventname]['tier 4']['person'],
            )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))


@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'loggedin' in session:
        return render_template(
            'personal.html',
            session=session['loggedin'],
            name=session['username'],
        )
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
