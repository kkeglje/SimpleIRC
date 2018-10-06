from flask import Flask,render_template,session,flash,url_for,redirect,request
from functools import wraps
import os
from form import RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['DATABASE_FILE'] = 'users.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =======CLASSES=======
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))
    admin = db.Column(db.String(5))

    # # Flask-Login integration
    # def is_authenticated(self):
    #     return True

    # def is_active(self):
    #     return True

    # def is_anonymous(self):
    #     return False
    
    # def get_id(self):
    #     return self.id

    def __repr__(self):
        return '<User %r>' % self.username

# =======Functions=======
def test_db():
    db.drop_all()
    db.create_all()
    test = User(username="test",email="test@test.test",password=generate_password_hash("test")[20:],admin="True")
    db.session.add(test)
    db.session.commit()



def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args,**kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('home'))
    return wrap

def admin_required(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if session['admin']==True:
            return test(*args,**kwargs)
        else:
            return 'You are not authorized to access that site! <a href="/">Go back</a>'
    return wrap

# =======APP.ROUTE========


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')

@app.route('/login',methods=['POST'])
def login():
    formName = request.form['username']
    formPassword = request.form['password']
    user = User(username=formName,password=formPassword)
    quer = User.query.filter_by(username=formName).first()
    if quer == None:
        session['logged_in'] = False
        session['admin'] = False
        return home()
    if check_password_hash("pbkdf2:sha256:50000$"+quer.password,user.password):
        if quer.admin == "True":
            session['admin'] = True
        else: 
            session['admin'] = False    
        session['logged_in'] = True
        return home()
    else:
        session['logged_in'] = False
        session['admin'] = False
        return home()

    print('Username: {}\nPassword: {}'.format(formName,formPassword))
    

@app.route('/registration',methods=['GET','POST'])
def reg():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('Registration/registration.html',form=form)
        else:
            user = User(admin="False",username=form.username.data,email=form.email.data,password=generate_password_hash(form.password.data)[20:])
            db.session.add(user)
            db.session.commit()
            return render_template('home.html')
    else:
        return render_template('Registration/registration.html',form=form)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in',None)
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/show_users')
@admin_required
def show_users():
    return render_template('show_users.html',User=User.query.all())

def startServer():
    print("Checking for database..")
    app_dir = os.path.realpath(os.path.dirname(__file__))
    db_path = os.path.join(app_dir,app.config['DATABASE_FILE'])
    if not os.path.exists(db_path):
        print("""
        ------------------------------------
        Cannot find db..Building test base..
        ------------------------------------
        """)
        test_db()
    else:
        print("Found database!..\n")
    app.run(host='0.0.0.0',debug=True)
