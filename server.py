from flask import Flask, render_template, session, flash, url_for, redirect, request as frequest, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import random, string, time, os, json #OpenSSL
from utils import utilities


app = Flask(__name__)
app.secret_key = "SESSION_RANDOM_KEY_CHANGE_THIS_IN_PRODUCTION"
app.config['APP_DIR'] = os.path.realpath(os.path.dirname(__file__))

ALL_users = []
channels = []

# Classes
class User():
    def __init__(self,username,admin,password,email):
        '''
        username[string],
        admin[string(True or False)],
        password[hashed str],
        email[string]
        '''
        self.username = username
        self.admin = admin
        self.password = password
        self.email = email

    def makeAdmin(self):
        if not self.admin: self.admin = True
        else: print("Already an admin")

    def removeAdmin(self):
        if self.admin: self.admin = False
        else: print("Already not admin")

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Channel():
    '''
    name[string],
    admins[array of strings]
    users[array of strings]
    '''
    def __init__(self,name,admins,users):
        self.name = name
        self.messages = [{'name':name,'time': time.strftime("%Y:%m:%d:%H:%M:%S"),'msg':'Welcome to {}'.format(name)}]
        self.admins = admins
        self.users = users

    def saveMessages(self):
        print("TODO: save messages to " + self.name)
    
    def addMessage(self,name,time,message):
        '''
        Adds message to channel
        name[string]
        time[array build like Y,d,m,H,M]
        message[actual message]
        '''
        self.messages.append({'name': name,'time': ':'.join(time), 'msg':message})

    def __repr__(self):
        return self.name


# ========Auth=========
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args,**kwargs)
        else:
            return render_template(
                    '401.html',
                    error=jsonify({
                            'status': 401,
                            'message': 'Please login'
                        })
                    )    
    return wrap


# =======APP.ROUTE========
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/addUser',methods=['POST'])
def addUser():
    if frequest.method == 'POST':
        uname = json.loads(frequest.data.decode())['guestName']
        for u in ALL_users:
            if u == uname:
                return jsonify({
                    'message' : 'Already user with that name [{}]'.format(uname)
                })
        ALL_users.append(uname)
        print("Appended %s" % uname)
        channels[0].users.append(uname)
        return jsonify({
            'status' : 200,
            'message' : 'Success',
            'user' : uname
        })
    else:
        return jsonify({
            'status' : 401,
            'message' : 'Please use POST request'
        })

@app.route('/getUsers',methods=['GET'])
def getUsers():
    return jsonify({
        'users' : ALL_users
    })


@app.route('/removeUser',methods=['POST'])
def removeUser():
    if frequest.method == 'POST':
        uname = json.loads(frequest.data.decode())['guestName']
        ALL_users.remove(uname)
        return jsonify({
            'status':200
        })
    else:
        return jsonify({
            'status' : 401,
            'message' : 'Please use POST request'
        })

@app.route('/getMessages',methods=['GET'])
def getMessages():
    # print("0-------------------0")
    # print(frequest.data.decode())
    # print("0-------------------0")
    chan = frequest.args.get('channel') #
    for c in channels:
        if c.name==chan:
            return jsonify({
                'messages': c.messages
            })
    else: return jsonify({
                'status': 400,
                'message': "There is no channel named %s" % channel
            })


@app.route('/addMessage',methods=['POST'])
def addMessage():
    if frequest.method == 'POST':
        channel = json.loads(frequest.data.decode())['channel']
        usr = json.loads(frequest.data.decode())['name']
        message = json.loads(frequest.data.decode())['msg']
        time = json.loads(frequest.data.decode())['time']
        time = str(time).split(':') #Y:d:m:H:M:s
        print("Adding message {0} to channel {1} from user {2} [{3}]".format(message,channel,usr,':'.join(time)))
        for c in channels:
            if c.name==channel:
                c.addMessage(usr,time,message)
                return jsonify({
                    'status': 200,
                    'message': 'Added message'
                })
        else: return jsonify({
                'status': 400,
                'message': "There is no channel named %s" % channel
            })
    else:
        return jsonify({
            'status' : 401,
            'message' : 'Please use POST request'
        })

@app.route('/addChannel',methods=['POST'])
def addChannel():
    if frequest.method == 'POST':
        channel = json.loads(frequest.data.decode())['channel']
        if channel in channels:
            return jsonify({
                'status': 400,
                'message': 'Already channel with that name'
            })
        else:
            channels.append(Channel(channel,[],[]))
            return jsonify({
                'status': 201,
                'message': 'Created new channel {0}'.format(channel)
            })
    else:
        return jsonify({
            'status' : 401,
            'message' : 'Please use POST request'
        })

@app.route('/getChannels',methods=['GET'])
def getChannels():
    return jsonify({
        'channels': '|'.join((x.name for x in channels))
    })


def startServer():
    print("    <<Starting server>>")
    channels.extend([Channel("Home",[],[]),Channel("Learning",[],[])])
    
    #TODO:
    #print("<<Generating session keys>>")
    #generateRoomKeys()

    app.run(host='0.0.0.0', debug=True)

