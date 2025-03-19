from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime, timedelta
from functools import wraps
import math

app = Flask(__name__)
app.secret_key = '231ad3242e231b2132b214034bbca3'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

events_available = ['birthday', 'anniversary', 'other']

pricing = {
    'birthday': {
        'tier1': {'base': 7500, 'person': 750},
        'tier2': {'base': 10000, 'person': 1000},
        'tier3': {'base': 12500, 'person': 1250},
        'tier4': {'base': 17000, 'person': 1550},
    },
    'anniversary': {
        'tier1': {'base': 9000, 'person': 1000},
        'tier2': {'base': 12000, 'person': 1300},
        'tier3': {'base': 15000, 'person': 1600},
        'tier4': {'base': 20000, 'person': 1900},
    },
    'other': {
        'tier1': {'base': 8000, 'person': 875},
        'tier2': {'base': 11000, 'person': 1150},
        'tier3': {'base': 14000, 'person': 1400},
        'tier4': {'base': 18500, 'person': 1700},
    },
}

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

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
        cursor.execute(
            '''
            SELECT p.*, TIMESTAMPDIFF(YEAR, dob, CURDATE()) AS age, c.* 
            FROM personal p NATURAL JOIN contact c 
            WHERE pid = (SELECT pid FROM has WHERE uid = (SELECT uid FROM users WHERE username = %s))
            ''',
            [session['username']],
        )
        personal_details = cursor.fetchone()
        cursor.execute(
            '''
            SELECT COUNT(eid) as count 
            FROM books 
            WHERE uid = (SELECT uid FROM users WHERE username = %s)
            ''',
            [session['username']],
        )
        count_event = cursor.fetchone()
        cursor.execute(
            '''
            SELECT e.*, b.* 
            FROM event e NATURAL JOIN books b 
            WHERE e.eid IN (SELECT eid FROM books WHERE uid = (SELECT uid FROM users WHERE username = %s))
            ''',
            [session['username']],
        )
        event_details = cursor.fetchall()
        return render_template(
            'dashboard.html',
            name=username,
            pdata=personal_details,
            cn=count_event,
            events=event_details,
        )
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor() 
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = MD5(%s)", (username, password)
        )
        account = cursor.fetchone()

        if account:
            last_login = datetime.now() 
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = 'user'  # Assuming regular users have 'user' role
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE username=%s",
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
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", [username])
            account = cursor.fetchone()

            if account:
                rmsg = "Username already exists!"
                return render_template("register.html", rmsg=rmsg)
            else:
                cursor.execute(
                    "INSERT INTO users(username,password,email,role,created_at) VALUES(%s,MD5(%s),%s,'user',NOW())",
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
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/<eventname>', methods=['GET', 'POST'])
def book_event(eventname: str):
    if request.method == 'POST':
        ev = request.form
        person1 = person2 = None
        if eventname == 'birthday':
            person1 = ev['person1']
            etype = 'Birthday'
        elif eventname == 'anniversary':
            person1 = ev['person1']
            person2 = ev['person2']
            etype = 'Anniversary'
        else:
            etype = ev['etype']
        venue = ev['venue']
        tier = ev['tier']
        max_people = ev['max']
        date = ev['edate']
        requests = ev['requests']
        
        # Check if there's already any event on the selected date
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM event WHERE edate = %s",
            (date,)
        )
        existing_event = cursor.fetchone()
        
        if existing_event:
            # If there's an existing event on the date, show error message
            error_message = f"There's already an event scheduled on {date}. Please choose another date."
            return render_template(
                'booking.html',
                session=session['loggedin'],
                name=session['username'],
                event=eventname.capitalize(),
                t1_base=pricing[eventname]['tier1']['base'],
                t2_base=pricing[eventname]['tier2']['base'],
                t3_base=pricing[eventname]['tier3']['base'],
                t4_base=pricing[eventname]['tier4']['base'],
                t1_per=pricing[eventname]['tier1']['person'],
                t2_per=pricing[eventname]['tier2']['person'],
                t3_per=pricing[eventname]['tier3']['person'],
                t4_per=pricing[eventname]['tier4']['person'],
                error_message=error_message
            )
        
        cost = (
            int(max_people) * pricing[eventname][tier]['person'] + pricing[eventname][tier]['base']
        )
        if tier == 'tier1':
            tier = 1
        elif tier == 'tier2':
            tier = 2
        elif tier == 'tier3':
            tier = 3
        elif tier == 'tier4':
            tier = 4
        
        # If no existing event on the date, proceed with booking
        cursor.execute(
            '''
            INSERT INTO event(etype, edate, etier, ecost, evenue, emax_people, especial, status)
            VALUES(%s,%s,%s,%s,%s,%s,%s,'pending')
            ''',
            (etype, date, tier, cost, venue, max_people, requests),
        )
        cursor.execute(
            '''
            INSERT INTO books VALUES(
                (SELECT uid FROM users WHERE username=%s),
                (SELECT LAST_INSERT_ID()),
                %s,%s)
            ''',
            (session['username'], person1, person2),
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard', username=session['username']))

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
                t1_base=pricing[eventname]['tier1']['base'],
                t2_base=pricing[eventname]['tier2']['base'],
                t3_base=pricing[eventname]['tier3']['base'],
                t4_base=pricing[eventname]['tier4']['base'],
                t1_per=pricing[eventname]['tier1']['person'],
                t2_per=pricing[eventname]['tier2']['person'],
                t3_per=pricing[eventname]['tier3']['person'],
                t4_per=pricing[eventname]['tier4']['person'],
            )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))

@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute(
        '''
        SELECT p.* ,c.*  
        FROM personal p NATURAL JOIN contact c 
        WHERE pid = (SELECT pid from has where uid = (SELECT uid from users where username=%s))
        ''',
        [session['username']],
        )
        details = cursor.fetchone()
        cursor.close()
        if request.method == "POST":
            firstname = request.form['fname']
            middlename = request.form['mname']
            lastname = request.form['lname']
            DOB = request.form['dob']
            contact1 = request.form['contact1']
            contact2 = request.form['contact2']
            contact3 = request.form['contact3']
            gender = request.form['gender']
            address = request.form['address']
            cursor = mysql.connection.cursor()
            cursor.execute(
                '''
                    SELECT * FROM has WHERE uid = 
                    (SELECT uid FROM users WHERE username = %s)
                ''',
                [session['username']],
            )
            personal_exists = cursor.fetchone()
            if personal_exists:
                cursor.execute(
                    '''
                    UPDATE personal SET
                    fname=%s,
                    mname=%s,
                    lname=%s,
                    dob=%s,
                    gender=%s,
                    address=%s 
                    WHERE pid =
                    (SELECT pid FROM has WHERE uid = 
                    (SELECT uid FROM users WHERE username=%s))
                    ''',
                    (
                        firstname,
                        middlename,
                        lastname,
                        DOB,
                        gender.capitalize(),
                        address,
                        session['username'],
                    ),
                )
                cursor.execute(
                    '''
                    UPDATE contact SET
                    contact1=%s,
                    contact2=%s,
                    contact3=%s
                    WHERE pid=
                    (SELECT pid FROM has WHERE uid = 
                    (SELECT uid FROM users WHERE username=%s))
                    ''',
                    (contact1, contact2, contact3, session['username']),
                )
            else:
                cursor.execute(
                    '''
                    INSERT INTO
                    personal(fname,mname,lname,dob,gender,address) 
                    VALUES(%s,%s,%s,%s,%s,%s)
                    ''',
                    (firstname, middlename, lastname, DOB, gender.capitalize(), address),
                )
                cursor.execute(
                    '''
                    INSERT INTO contact VALUES(
                        (SELECT LAST_INSERT_ID()),
                        %s, %s, %s
                    )
                    ''',
                    (contact1, contact2, contact3),
                )
               
                cursor.execute(
                    '''
                    INSERT INTO has VALUES(
                        (SELECT uid FROM users WHERE username=%s),
                        (SELECT LAST_INSERT_ID())
                    )
                    ''',
                    [session['username']],
                )
            mysql.connection.commit()
            cursor.close()
            
            return redirect(url_for('dashboard', username=session['username']))
        return render_template(
            'personal.html', session=session['loggedin'], name=session['username'], details=details
        )
    else:
        return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = MD5(%s) AND role = 'admin'", 
            (username, password)
        )
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = 'admin'
            cursor.close()
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template("admin_login.html", msg="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    cursor = mysql.connection.cursor()
    
    # Update event statuses based on current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        """
        UPDATE event 
        SET status = CASE 
            WHEN edate < %s THEN 'completed'
            WHEN edate >= %s THEN 'pending'
            ELSE status
        END
        """,
        (current_date, current_date)
    )
    mysql.connection.commit()
    
    # Basic statistics
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute("SELECT COUNT(*) as total_events FROM event")
    total_events = cursor.fetchone()['total_events']
    
    cursor.execute("SELECT SUM(ecost) as total_revenue FROM event")
    total_revenue = cursor.fetchone()['total_revenue'] or 0
    
    cursor.execute("SELECT AVG(ecost) as avg_event_cost FROM event")
    avg_event_cost = cursor.fetchone()['avg_event_cost'] or 0
    
    # User growth statistics
    cursor.execute("""
        SELECT COUNT(*) as users_last_7_days 
        FROM users 
        WHERE DATE(last_login) >= CURDATE() - INTERVAL 7 DAY
    """)
    users_last_7_days = cursor.fetchone()['users_last_7_days']
    
    cursor.execute("""
        SELECT COUNT(*) as events_last_month 
        FROM event 
        WHERE edate >= CURDATE() - INTERVAL 1 MONTH
    """)
    events_last_month = cursor.fetchone()['events_last_month']
    
    # Growth percentages (simplified - you might want to adjust these calculations)
    cursor.execute("SELECT COUNT(*) as total_users_last_week FROM users WHERE DATE(last_login) >= CURDATE() - INTERVAL 7 DAY")
    total_users_last_week = cursor.fetchone()['total_users_last_week'] or 1
    user_growth = round((users_last_7_days - total_users_last_week) / total_users_last_week * 100, 2)
    
    cursor.execute("SELECT COUNT(*) as total_events_last_week FROM event WHERE edate >= CURDATE() - INTERVAL 7 DAY")
    total_events_last_week = cursor.fetchone()['total_events_last_week'] or 1
    event_growth = round((events_last_month - total_events_last_week) / total_events_last_week * 100, 2)
    
    cursor.execute("SELECT SUM(ecost) as total_revenue_last_week FROM event WHERE edate >= CURDATE() - INTERVAL 7 DAY")
    total_revenue_last_week = cursor.fetchone()['total_revenue_last_week'] or 1
    revenue_growth = round((total_revenue - total_revenue_last_week) / total_revenue_last_week * 100, 2)
    
    # Top events
    cursor.execute("""
        SELECT etype, COUNT(*) as count 
        FROM event 
        GROUP BY etype 
        ORDER BY count DESC 
        LIMIT 5
    """)
    top_events = cursor.fetchall()
    
    # Recent users
    cursor.execute("SELECT * FROM users ORDER BY last_login DESC LIMIT 5")
    recent_users = cursor.fetchall()
    
    # Data for charts
    cursor.execute("""
        SELECT DATE(edate) as date, COUNT(*) as count 
        FROM event 
        WHERE edate >= CURDATE() - INTERVAL 30 DAY
        GROUP BY DATE(edate)
        ORDER BY date
    """)
    bookings_data = cursor.fetchall()
    bookings_labels = [str(row['date']) for row in bookings_data]
    bookings_data_values = [row['count'] for row in bookings_data]
    
    cursor.execute("""
        SELECT etype, SUM(ecost) as revenue 
        FROM event 
        GROUP BY etype 
        ORDER BY revenue DESC
    """)
    revenue_data = cursor.fetchall()
    revenue_labels = [row['etype'] for row in revenue_data]
    revenue_data_values = [row['revenue'] for row in revenue_data]
    
    # User registrations over time
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM users 
        WHERE created_at >= CURDATE() - INTERVAL 30 DAY
        GROUP BY DATE(created_at)
        ORDER BY date
    """)
    user_reg_data = cursor.fetchall()
    user_reg_labels = [str(row['date']) for row in user_reg_data]
    user_reg_data_values = [row['count'] for row in user_reg_data]
    
    # Event status data
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM event 
        GROUP BY status
    """)
    event_status_data = cursor.fetchall()
    event_status_labels = [row['status'] for row in event_status_data]
    event_status_data_values = [row['count'] for row in event_status_data]
    
    # Additional statistics
    cursor.execute("SELECT COUNT(*) as completed_events FROM event WHERE status = 'completed'")
    completed_events = cursor.fetchone()['completed_events']
    
    cursor.execute("SELECT COUNT(*) as pending_events FROM event WHERE status = 'pending'")
    pending_events = cursor.fetchone()['pending_events']
    
    cursor.execute("""
        SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, edate)) as avg_booking_time 
        FROM event 
        JOIN books ON event.eid = books.eid
        JOIN users ON books.uid = users.uid
    """)
    avg_booking_time = cursor.fetchone()['avg_booking_time'] or 0
    
    # Recent events
    cursor.execute("""
        SELECT e.*, u.username, e.status 
        FROM event e 
        JOIN books b ON e.eid = b.eid
        JOIN users u ON b.uid = u.uid
        ORDER BY e.edate DESC 
        LIMIT 10
    """)
    recent_events = cursor.fetchall()
    
    # User list with event counts
    cursor.execute("""
        SELECT u.*, COUNT(b.eid) as event_count 
        FROM users u 
        LEFT JOIN books b ON u.uid = b.uid
        GROUP BY u.uid
    """)
    users = cursor.fetchall()
    
    cursor.close()
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_events=total_events,
        total_revenue=total_revenue,
        avg_event_cost=avg_event_cost,
        users_last_7_days=users_last_7_days,
        events_last_month=events_last_month,
        user_growth=user_growth,
        event_growth=event_growth,
        revenue_growth=revenue_growth,
        top_events=top_events,
        recent_users=recent_users,
        users=users,
        bookings_labels=bookings_labels,
        bookings_data=bookings_data_values,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data_values,
        user_reg_labels=user_reg_labels,
        user_reg_data=user_reg_data_values,
        event_status_labels=event_status_labels,
        event_status_data=event_status_data_values,
        completed_events=completed_events,
        pending_events=pending_events,
        avg_booking_time=avg_booking_time,
        recent_events=recent_events
    )

@app.route('/admin/delete_user', methods=['POST'])
@admin_login_required
def delete_user():
    user_id = request.form['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE uid = %s", [user_id])
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    rmsg = ""
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        email = userDetails['email']
        repass = userDetails['reenterPassword'] 
        if password != repass:
            rmsg = "Password does not match!"
            return render_template("admin_register.html", rmsg=rmsg)
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", [username])
            account = cursor.fetchone()

            if account:
                rmsg = "Username already exists!"
                return render_template("admin_register.html", rmsg=rmsg)
            else:
                cursor.execute(
                    "INSERT INTO users(username,password,email,role,created_at) VALUES(%s,MD5(%s),%s,'admin',NOW())",
                    (username, password, email),
                )
                mysql.connection.commit()
                cursor.close()
            return redirect(url_for('admin_login'))
    return render_template('admin_register.html')

if __name__ == '__main__':
    app.run(debug=True)