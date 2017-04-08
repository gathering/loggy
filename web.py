import os, json, logging, datetime, hashlib, urllib2
from flask import Flask, render_template, request, session, escape, request, abort, redirect, url_for
from config import Config

class Web:

    #Holy #### this is not best practise! :-) Please ignore
    global readJson
    global getChannels
    global app
    global shutdown_server
    global createDateList
    global createDate
    global channelDate
    global config
    global checkLogin
    global apiLogin
    global doLogin
    global checkAdmin
    global checkUsername
    global getAllUsers
    global addUser

    app = Flask(__name__)

    config = Config()
    app.secret_key = config.getSecretKey()

    def apiLogin(username, password):
        url = config.getApiUrl();
        parameters = "?app="+config.getAppKey()
        md5 = hashlib.md5(password).hexdigest()
        login_parameters = "&username="+username+"&password="+md5
        requestUrl = ""+url+parameters+login_parameters
        try:
            r = urllib2.urlopen(requestUrl)
        except:
            return False

        data = json.loads(r.read())
        if 'error' in data:
            return False
        else:
            return True

    def checkLogin():
        if config.getAuth():
            if 'username' in session:
                return True
            else:
                return False
        else:
            session['username'] = "dummy"
            session['admin'] = False
            return True

    def checkUsername(username):
        with open('users.json') as f:
            data = json.load(f)
        result = False
        for d in data:
            if d['username'] == username:
                result = True
        return result

    def checkAdmin(username):
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

    def addUser(username, isAdmin):
        print("Added user "+username+" which is admin: "+isAdmin)
        a_dict = {"username": username,"isAdmin": isAdmin}

        data = []
        try:
            with open('users.json') as f:
                data = json.load(f)
        except:
            pass

        data.append(a_dict)

        with open('users.json', 'w') as f:
            json.dump(data, f)

    def getAllUsers():
        with open('users.json') as f:
            data = json.load(f)
        return data


    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def readJson(channel):
        with open('logs/'+channel+'.json') as f:
            data = json.load(f)
        return data

    def createDate(date):
        wdate = datetime.datetime.strptime(date, '%c').strftime('%y%m%d')
        return wdate

    def createDateList(channel):
        with open('logs/'+channel+'.json') as f:
            data = json.load(f)

        #First, we find all uniqe dates.
        dates = []
        for d in data:
            dates.append(createDate(d['date']))
        dateset = set(dates)

        dates = []
        for date in dateset:
            readable = datetime.datetime.strptime(date, '%y%m%d').strftime('%A %d. %b %Y')
            dates.append([date, readable])

        return reversed(sorted(dates, key=lambda dates: dates[0]))

    def channelDate(channel, date):
        with open('logs/'+channel+'.json') as f:
            data = json.load(f)
        sort = []
        for d in data:
            curdate = createDate(d['date'])
            if curdate == date:
                sort.append(d)

        return sort

    def getChannels():
        ch = []
        for file in os.listdir("logs"):
            if file.endswith(".json"):
                ch.append(file.replace(".json", ""))
        return ch

    def doLogin(username, password):
        if apiLogin(username, password):
            if checkUsername(username):
                session['username'] = username
                session['admin'] = checkAdmin(username)
                print("Logged in "+username+" with admin: "+str(checkAdmin(username)))
                return True
        else:
            return False


    @app.route('/users', methods=['GET', 'POST'])
    def users():
        if checkLogin():
            if session['admin'] == True:
                if request.method == 'POST':
                    addUser(request.form['username'], request.form['isAdmin'])
                    return redirect(url_for('users'))
                else:
                    return render_template('users.html', users=getAllUsers())
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
                state = doLogin(request.form['username'], request.form['password'])
                return redirect(url_for('index'))
            else:
                return redirect(url_for('index'))
        else:
            if checkLogin():
                return render_template('index.html', result=getChannels(), isAdmin=session['admin'])
            else:
                return render_template('login.html')

    @app.route('/channel/<name>')
    def channel(name):
        if checkLogin():
            return render_template('channel.html', name=name, result=reversed(readJson(name)), dates=createDateList(name))
        else:
            abort(403)

    @app.route('/channel/<name>/<date>')
    def channelDateRoute(name, date):
        if checkLogin():
            readable=datetime.datetime.strptime(date, '%y%m%d').strftime('%A %d. %b %Y')
            return render_template('channel.html', name=name, result=reversed(channelDate(name, date)), dates=createDateList(name), readable=readable)
        else:
            abort(403)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('error.html'), 500

    @app.errorhandler(403)
    def needtologin(e):
        return redirect(url_for('index'))

    def startWeb(args):
        logger = logging.getLogger('werkzeug')
        handler = logging.FileHandler('debug/access.log')
        logger.addHandler(handler)
        app.run(debug=False, host='0.0.0.0', threaded=True)
