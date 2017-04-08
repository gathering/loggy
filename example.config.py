'''

Please make sure to rename this file to "config.py" and enter correct details in this file.

'''

import os

class Config:
    global BOT_ID
    global SLACK_ID
    global WEB_URL
    global API_URL
    global APP_KEY
    global AUTH_EN
    global SECRET_KEY

    ######
    # EDIT BELOW THIS LINE
    ######

    BOT_ID = "" #CHANGE THIS TO THE BOT USER ID
    SLACK_ID = "" #CHANGE THIS TO THE SLACK API ID
    WEB_URL = "" # USED TO RETURN TO USER WHERE TO FIND LOGS IN HELP MENU
    API_URL = "" # API URL
    APP_KEY = "" # APP KEY
    AUTH_EN = "" # ENABLE AUTH. True or False
    SECRET_KEY = "" #Random secret key, used for sessions. You can generate one in python with os.urandom(24)

    ######
    # DO NOT EDIT BELOW THIS LINE
    ######

    def getBOT_ID(args):
        return BOT_ID

    def getSLACK_ID(args):
        return SLACK_ID

    def getWebURL(args):
        return WEB_URL

    def getAppKey(args):
        return APP_KEY

    def getApiUrl(args):
        return API_URL

    def getAuth(args):
        return AUTH_EN

    def getSecretKey(args):
        return SECRET_KEY
