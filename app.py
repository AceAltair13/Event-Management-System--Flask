# This is sample text to be merged into master branch

from flask import Flask,render_template,redirect,url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField
from wtforms.validators import InputRequired,Email,Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = "Thisissupposedtobesecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db= SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15),unique=True)
    email = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

class LoginForm(FlaskForm):
    username = StringField('Username',validators =[InputRequired(),Length(min=4,max=80)])
    password = PasswordField('Password',validators=[InputRequired(),Length(min=8,max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email',validators=[InputRequired(),Email(message="Invalid Email"),Length(max=50)])
    username = StringField('Username',validators = [InputRequired(), Length(min=4,max=15)])
    password = PasswordField('Password',validators=[InputRequired(), Length(min=8,max=80)])
    re_enter = PasswordField('Re-enter Password',validators=[InputRequired(), Length(min=8,max=80)])

 

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/users/')
@login_required
def dashboard():
    return render_template('dashboard.html',events=registered_events,name=current_user.username)

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    #return render_template('login.html',form=form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user,remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return '<h1> Invalid username or password </h1>'
    
    return render_template('login.html',form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    
    if form.validate_on_submit(): #Checks if the form has been submitted or not
       #return '<h1>' + form.username.data + '<br>' + form.password.data + '<h2>'
        hashed_password = generate_password_hash(form.password.data,method = 'sha256')
        new_user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New user has been created</h1>'
    
    return render_template('register.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)