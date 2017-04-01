import os, json, logging
from flask import Flask, render_template

class Web:

    global readJson
    global getChannels
    global app
    global shutdown_server

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
    def hello(name):
        return render_template('channel.html', name=name, result=reversed(readJson(name)))

    def startWeb(args):
        logger = logging.getLogger('werkzeug')
        handler = logging.FileHandler('debug/access.log')
        logger.addHandler(handler)
        app.run(debug=False, host='0.0.0.0', threaded=True)
