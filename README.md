<img src="/static/loggbot.png?raw=true" height="100">

# loggerbot
A Slack bot with embedded web server for logging incidents from Slack.

## Below the hood
Based on Slacks own Slack Client for Python. Install with "pip install slackclient". Also uses Python Flask Webserver, install with "pip install Flask"

### The logs
The logs are saved in flatfile JSON files in the folder "json".

## First time slack-app and docker setup

1. Create a new slack app at: api.slack.com/apps
	1. Create new app and add to local/developer workspace
	1. Enable bot user under "Features > Bot users"
	1. Install App under "Settings > Install App"
	1. Make a note of your "Bot User OAuth Access Token" (xoxb-...)
1. Create and populate config.py
	1. SLACK_ID; Your "Bot User OAuth Access Token"
	1. BOT_ID; Not your bot user user, but a unique id returned by slack. Leave blank to try to autodetect
	1. WEB_URL; The public/private url to your web server (only used in "click here to read log" messages)
	1. API_URL
	1. APP_KEY
	1. AUTH_EN
	1. SECRET_KEY; Something completely random, change this to invalidate all existing sessions
1. Start container instance on your platform of choice

	# Just build the container
	docker build . --tag 'loggy'

	# ... or start non-persistent local container instance (bot will still be able to talk to the slack RTM API)
	cp example.docker-compose.yml docker-compose.yml
	docker-compose up
