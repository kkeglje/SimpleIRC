from flask import Flask,render_template,session,flash,url_for,redirect, request as frequest, jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import random, string, datetime, os


app = Flask(__name__)
app.secret_key = "SESSION_RANDOM_KEY_CHANGE_THIS_IN_PRODUCTION"
app.config['DATABASE_FILE'] = 'users.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APP_DIR'] = os.path.realpath(os.path.dirname(__file__))

db = SQLAlchemy(app)

ROOM_IDs = []

# =========CLASSES=========
class User(db.Model):
    '''
    username[string],
    admin[string(True or False)],
    password[hashed str],
    email[string]
    '''
    id = db.Column('user_id',db.Integer,primary_key=True)
    username = db.Column(db.String(16), unique=True,nullable=False)
    admin = db.Column(db.String(5))
    password = db.Column(db.String(64),nullable=False)
    email = db.Column(db.String(64),nullable=False)
    def __repr__(self):
        return '<User {}>'.format(self.username)

# =======Functions=======
def test_db():
    db.drop_all()
    db.create_all()
    test = User(username="admin",email="admin@admin",password=generate_password_hash("admin")[20:],admin="True")
    db.session.add(test)
    db.session.commit()

def generateRoomKeys():
    global ROOM_IDs
    f = open("roomKeys.txt",'w')
    for w in range(100):
        s=[]
        for l in range(16):
            s.append(string.ascii_letters[random.randint(0,51)])
        ROOM_IDs.append(''.join(s))
    print("Session keys generated and saved in roomKeys.txt")
    f.write("SESSION KEYS GENERATED "+str(datetime.datetime.now())[:-7]+"\n--------\n"+'\n'.join(ROOM_IDs))
    f.close()


# ========Auth=========
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

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if frequest.method == 'POST':
        uname = frequest.form['username']
        passw = frequest.form['password']

        if uname=="test":
            print("test")
        t = User.query.filter_by(username=uname).first()
        if t==None:
            error = "There is no user with that name"
        elif t.admin == "True" and check_password_hash("pbkdf2:sha256:50000$"+t.password,passw):
            session['admin'] = True
            session['logged_in'] = True
            return redirect(url_for('home'))
        elif check_password_hash("pbkdf2:sha256:50000$"+t.password,passw):
            session['logged_in'] = True
            session['admin'] = False
            return redirect(url_for('home'))
        else:
            error = "Wrong username/password"
    return render_template('login.html',error=error)
 

@app.route('/registration',methods=['GET','POST'])
def registration():
    error = None
    if frequest.method == 'POST':
        uname = frequest.form['username']
        passw = frequest.form['password']
        rpassw = frequest.form['rpassword']
        email = frequest.form['email']
        setToAdmin = "False"
        if frequest.form.get('admin'):
            setToAdmin = "True"
        if User.query.filter_by(username=uname).first() != None:
            error = ""
            return render_template(
                    'registration.html',
                    error=jsonify({
                            'status': 400,
                            'message': 'Username already taken!'
                        })
                    )
        elif User.query.filter_by(email=email).first() != None:
            return render_template(
                    'registration.html',
                    error=jsonify({
                            'status': 400,
                            'message': 'Email already taken!'
                        })
                    )
        elif passw!=rpassw:
            return render_template(
                    'registration.html',
                    error=jsonify({
                            'status': 400,
                            'message': 'Your passwords dont match'
                        })
                    )    
        if uname == "" or passw == "" or email == "":
            return render_template(
                        'registration.html',
                        error=jsonify({
                            'status': 400,
                            'message': 'Please fill in empty fields'
                            })
                        )
        u = User(username=uname,email=email, admin=setToAdmin ,password=generate_password_hash(passw)[20:])        
        db.session.add(u)
        db.session.commit()
        backup_db(User,Food)
        print("Backup complete!")
        return redirect(url_for('success'))
    else:
        return render_template('registration.html',error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in',False)
    session.pop('admin', False)
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
@app.errorhandler(404)
def not_found():
    return "This is a 404 page(work in progress)"


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
    generateRoomKeys()

    app.run(host='0.0.0.0',debug=True)
