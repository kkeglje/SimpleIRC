from flask import Flask,render_template,session,flash,url_for,redirect,request
from functools import wraps
import os
from form import RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import random, string,datetime


app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['DATABASE_FILE'] = 'users.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APP_DIR'] = os.path.realpath(os.path.dirname(__file__))
db = SQLAlchemy(app)
ROOM_IDs = []


# =======CLASSES=======
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))
    admin = db.Column(db.String(5))

    def __repr__(self):
        return '<User %r>' % self.username

# =======Functions=======
def test_db():
    db.drop_all()
    db.create_all()
    test = User(username="test",email="test@test.test",password=generate_password_hash("test")[20:],admin="True")
    db.session.add(test)
    db.session.commit()

def generateSessionKeys():
    global ROOM_IDs
    f = open("sessionKeys.txt",'w')
    for w in range(100):
        s=[]
        for l in range(16):
            s.append(string.ascii_letters[random.randint(0,51)])
        ROOM_IDs.append(''.join(s))
    print("Session keys generated and saved in sessionKeys.txt")
    f.write("SESSION KEYS GENERATED "+str(datetime.datetime.now())[:-7]+"\n--------\n"+'\n'.join(ROOM_IDs))
    
    f.close()



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

@app.route('/chat')
@login_required
def chat():
    return render_template('Chat/lobby.html',User=User.query.all())

@app.route('/create_room',methods=['GET'])
@login_required
def create_room():
    global ROOM_IDs
    rn = random.randint(0,len(ROOM_IDs)-1)
    sess = ROOM_IDs[rn]
    ROOM_IDs.remove(sess)
    f = open(app.config['APP_DIR']+"/templates/Chat/key.html",'w')
    f.write("""<p>{}  <- this is your key, please copy it and send it to your friend\
    </p>\n<a href="/chat/{} ">Join room</a> """.format(sess,sess))
    f.close()
    return render_template('Chat/key.html')

    

@app.route('/chat/<room>',methods=['GET','POST'])
@login_required
def room(room):
    return "ROOM KEY= %s" % room



# =========ERROR HANDLERS=========

@app.errorhandler(401)
def unauthorized_access(e):
    return render_template('Errors/401.html'),401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('Errors/404.html'),404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('Errors/405.html'),405
# ===========================


def startServer():
    print(" <<Checking for database>>")
    db_path = os.path.join(app.config['APP_DIR'],app.config['DATABASE_FILE'])
    if not os.path.exists(db_path):
        print("<<Cannot find db>> ->Building test base..")
        test_db()
    else:
        print("    <<Found database>>")

    print("    <<Starting server>>")
    print("<<Generating session keys>>")
    generateSessionKeys()

    app.run(host='0.0.0.0',debug=True)
