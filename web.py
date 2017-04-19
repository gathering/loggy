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


def add_user(username, is_admin):
    print("Added user " + username + " which is admin: " + is_admin)
    a_dict = {"username": username, "isAdmin": is_admin}

    data = []
    try:
        with open('users.json') as f:
            data = json.load(f)
    except:
        pass

    data.append(a_dict)

    with open('users.json', 'w') as f:
        json.dump(data, f)


def get_all_users():
    with open('users.json') as f:
        data = json.load(f)
    return data


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
                return render_template('users.html', users=get_all_users())
        else:
            abort(403)
    else:
        abort(403)


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
