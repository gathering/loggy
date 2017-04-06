import os, json, logging, datetime
from flask import Flask, render_template

class Web:

    global readJson
    global getChannels
    global app
    global shutdown_server
    global createDateList
    global createDate
    global channelDate

    app = Flask(__name__)

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

        return sorted(dates, key=lambda dates: dates[0])

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

    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    @app.route('/')
    def index():
        return render_template('index.html', result=getChannels())

    @app.route('/channel/<name>')
    def channel(name):
        return render_template('channel.html', name=name, result=reversed(readJson(name)), dates=createDateList(name))

    @app.route('/channel/<name>/<date>')
    def channelDateRoute(name, date):
        readable=datetime.datetime.strptime(date, '%y%m%d').strftime('%A %d. %b %Y')
        return render_template('channel.html', name=name, result=reversed(channelDate(name, date)), dates=createDateList(name), readable=readable)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('error.html'), 500

    def startWeb(args):
        logger = logging.getLogger('werkzeug')
        handler = logging.FileHandler('debug/access.log')
        logger.addHandler(handler)
        app.run(debug=False, host='0.0.0.0', threaded=True)
