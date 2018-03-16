import datetime
import hashlib
import json
import logging
import os
import urllib2

from flask import Flask, render_template, session, request, abort, redirect, url_for, send_from_directory

import config

app = Flask(__name__)

app.secret_key = config.SECRET_KEY


def api_login(username, password):
    url = config.API_URL
    parameters = "?app=" + config.APP_KEY
    md5 = hashlib.md5(password).hexdigest()
    login_parameters = "&username=" + username + "&password=" + md5
    request_url = "" + url + parameters + login_parameters
    try:
        r = urllib2.urlopen(request_url)
    except:
        return False

    data = json.loads(r.read())
    if 'error' in data:
        return False
    else:
        return True


def check_login():
    if config.AUTH_EN:
        if 'username' in session:
            return True
        else:
            return False
    else:
        session['username'] = "dummy"
        session['admin'] = False
        return True


def check_username(username):
    with open('users.json') as f:
        data = json.load(f)
    result = False
    for d in data:
        if d['username'] == username:
            result = True
    return result


def check_admin(username):
    with open('users.json') as f:
        data = json.load(f)
    result = False
    for d in data:
        if d['username'] == username:
            result = d['isAdmin']
    if result == "False":
        return False
    else:
        return True

def load_users():
    try:
        with open('users.json') as f:
            data = json.load(f)
    except:
        print("Failed to open users file.")
    return data

def write_users(data):
    with open('users.json', 'w') as f:
        json.dump(data, f)


def add_user(username, is_admin):
    print("Added user " + username + " which is admin: " + is_admin)
    a_dict = {"username": username, "isAdmin": is_admin, "channels":[{"channel":"general", "admin":False}]}

    data = load_users()
    data.append(a_dict)
    write_users(data)


def get_all_users():
    with open('users.json') as f:
        data = json.load(f)
    return data

def get_user(username):
    allusers = load_users()
    i=0
    looking=True
    result=None
    while looking==True:
        if allusers[i]['username'] == username:
            result=allusers[i]
            looking=False
        else:
            i=i+1
    return result

def find_user_id(username):
    allusers = load_users()
    i=0
    looking=True
    result=-1
    while looking==True:
        if allusers[i]['username'] == username:
            result=i
            looking=False
        else:
            i=i+1
    return result

def find_channel_id_in_users_access(data, channel):
    looking=True
    result=-1
    i=0
    while looking==True:
        if data["channels"][i]['channel'] == channel:
            result=i
            looking=False
        else:
            i=i+1
    return result

def create_list_of_channels_which_user_is_admin_of(username):
    user=get_user(username)
    chlst=[]
    for channel in user[channels]:
        if channel['admin'] == True:
            chlist.append(channel["channel"])
    return chlst

def give_admin_to_channel(username, channel):
    allusers=load_users()
    userid=find_user_id(username)
    channelid=find_channel_id_in_users_access(allusers, channel)
    try:
        allusers[userid][channels][channelid]['admin']=True
        write_users(allusers)
    except:
        print("Could not add admin to channel")


def give_user_access_to_channel(username, channel, admin=False):
    allusers=load_users()
    userid=find_user_id(username)
    try:
        allusers[userid]["channels"].append({"channel":channel, "admin":admin})
    except:
        print("Could not add user to channel")
    write_users(allusers)


def check_access(username, channel):
    user = get_user(username)
    r=False
    try:
        if user['isAdmin'] == True:
            r=True
        else:
            channelid=find_channel_id_in_users_access(user, channel)
            if user["channels"][channelid]['admin'] == True:
                r=True
            else:
                r=False
    except Exception as e:
        print("ERROR: Failed to retrieve access for "+str(username)+" in channel "+str(channel)+". Error: "+str(e))
    return r

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def read_json(channel):
    with open('logs/' + channel + '.json') as f:
        data = json.load(f)
    return data


def create_date(date):
    wdate = datetime.datetime.strptime(date, '%c').strftime('%y%m%d')
    return wdate


def create_date_list(channel):
    with open('logs/' + channel + '.json') as f:
        data = json.load(f)

    # First, we find all uniqe dates.
    dates = []
    for d in data:
        dates.append(create_date(d['date']))
    date_set = set(dates)

    dates = []
    for date in date_set:
        readable = datetime.datetime.strptime(date, '%y%m%d').strftime('%A %d. %b %Y')
        dates.append([date, readable])

    return reversed(sorted(dates, key=lambda dates: dates[0]))


def channel_date(channel, date):
    with open('logs/' + channel + '.json') as f:
        data = json.load(f)
    sort = []
    for d in data:
        curdate = create_date(d['date'])
        if curdate == date:
            sort.append(d)

    return sort


def get_channels():
    ch = []
    for file in os.listdir("logs"):
        if file.endswith(".json"):
            ch.append(file.replace(".json", ""))
    return ch


def do_login(username, password):
    if api_login(username, password):
        if check_username(username):
            session['username'] = username
            session['admin'] = check_admin(username)
            print("Logged in " + username + " with admin: " + str(check_admin(username)))
            return True
    else:
        return False


@app.route('/users', methods=['GET', 'POST'])
def users():
    if check_login():
        if session['admin'] is True:
            if request.method == 'POST':
                add_user(request.form['username'], request.form['isAdmin'])
                return redirect(url_for('users'))
            else:
                return render_template('users.html', users=get_all_users(), user=get_user(session['username']))
        else:
            abort(403)
    else:
        abort(403)

@app.route('/users/<channel>')
def users_channel(channel):
    return channel

@app.route('/users/<channel>/add-user/<user>', methods=['GET'])
def web_add_admin_to_channel(channel, user):
    if session['admin'] or check_access(session['username'], channel):
        give_admin_to_channel(user, channel)
        return redirect(url_for("users"))
    else:
        return abort(403)

@app.route('/users/<channel>/add-admin/<user>', methods=['GET'])
def web_add_to_channel(channel, user):
    if check_access(session['username'], channel):
        give_user_access_to_channel(user, channel)
        return redirect(url_for("users"))
    else:
        return abort(403)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form['login']:
            state = do_login(request.form['username'], request.form['password'])
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        if check_login():
            return render_template('index.html', result=get_channels(), isAdmin=session['admin'])
        else:
            return render_template('login.html')


@app.route('/channel/<name>')
def show_channel(name):
    if check_login():
        return render_template('channel.html', name=name, result=reversed(read_json(name)),
                               dates=create_date_list(name))
    else:
        abort(403)


@app.route('/channel/<name>/<date>')
def channel_date_route(name, date):
    if check_login():
        readable = datetime.datetime.strptime(date, '%y%m%d').strftime('%A %d. %b %Y')
        return render_template('channel.html', name=name, result=reversed(channel_date(name, date)),
                               dates=create_date_list(name), readable=readable)
    else:
        abort(403)


@app.errorhandler(404)
def page_not_found(e):
    logging.debug(e.getMessage())
    return render_template('error.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    logging.debug(e.getMessage())
    return render_template('error.html'), 500


@app.errorhandler(403)
def need_to_login(e):
    logging.debug(e.getMessage())
    return redirect(url_for('index'))


def start_web():
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler('debug/access.log')
    logger.addHandler(handler)
    app.run(debug=False, host='0.0.0.0', threaded=True)
