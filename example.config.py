'''

Please make sure to rename this file to "config.py" and enter correct details in this file.

'''

import os

class Config:
    global BOT_ID
    global SLACK_ID

    ######
    # EDIT BELOW THIS LINE
    ######

    BOT_ID = "" #CHANGE THIS TO THE BOT USER ID
    SLACK_ID = "" #CHANGE THIS TO THE SLACK API ID

    ######
    # DO NOT EDIT BELOW THIS LINE
    ######

    def getBOT_ID(args):
        return BOT_ID

    def getSLACK_ID(args):
        return SLACK_ID
