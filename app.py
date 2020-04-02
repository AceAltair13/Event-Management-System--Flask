from flask import Flask,render_template
app = Flask(__name__)

registered_events=[
    {
        'event_name':"Yash's Birthday",
        'event_type': "Birthday",
        'event_location': "Kalyan",
        'organiser':"Yash",
        'date_booked': "2-Feb-2019",
    },
    {
        'event_name':"Throwback Party",
        'event_type': "Party",
        'event_location': "Mumbai",
        'organiser':"Tirth",
        'date_booked': "2-July-2019",
    },
    {
        'event_name':"XYZ's Anniversary",
        'event_type': "Anniversary",
        'event_location': "Ahmedabad",
        'organiser':"XYZ",
        'date_booked': "2-May-2019",
    }


]



@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/login/dashboard/')
def dashboard():
    return render_template('dashboard.html',events=registered_events)

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/register')
def register():
   return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)