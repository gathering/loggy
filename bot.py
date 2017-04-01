import os
import time
import json
from slackclient import SlackClient
from config import Config

class Bot:

    global slack_client
    global AT_BOT
    global appendToJson
    global handle_command
    global parse_slack_output
    global stop_bot
    global BOT_ID
    global slack_id

    config = Config()

    # loggbot's ID as an environment variable
    BOT_ID = config.getBOT_ID()

    # constants
    AT_BOT = "<@" + BOT_ID + ">"


    slack_client = SlackClient(config.getSLACK_ID())

    def appendToJson(text, channel, user):
        date = time.strftime("%c")
        import json
        a_dict = {"user": user,"date": date,"text": text}

        data = []
        try:
            with open('logs/'+channel+'.json') as f:
                data = json.load(f)
        except:
            pass

        data.append(a_dict)

        with open('logs/'+channel+'.json', 'w') as f:
            json.dump(data, f)


    def handle_command(command, channel, user, ts):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands.
            Retrieves some more info from the API if needed.
        """

        channelInfo = slack_client.api_call("channels.info", channel=channel)
        userInfo = slack_client.api_call("users.info", user=user)

        try:
            channelName = channelInfo['channel']['name']
        except:
            channelName = channel

        try:
            userNick = userInfo['user']['name']
        except:
            userNick = user

        try:
            realName = userInfo['user']['profile']['real_name']

        except:
            realName = None

        if realName != None:
            userNick = realName + " ("+userNick+")"

        appendToJson(command, channelName, userNick)
        response = "Hello "+userNick+"! You wrote: "+command
        slack_client.api_call("reactions.add",channel=channel, name="memo", timestamp=ts, as_user=True)


    def parse_slack_output(slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip(), \
                           output['channel'], \
                           output['user'], \
                           output['ts']
        return None, None, None, None


    def startBot(args):
        READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            print(" * LoggBot is connected to Slack and running!")
            while True:
                command, channel, user, ts = parse_slack_output(slack_client.rtm_read())
    #            username = request.form.get('user_name')
                if command and channel:
                    handle_command(command, channel, user, ts)
                time.sleep(READ_WEBSOCKET_DELAY)
    #            print(slack_client.rtm_read())
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

    def stop_bot(self):
        print "Trying to stop thread "
        if self.process is not None:
            self.process.terminate()
            self.process = None
