import time
from slackclient import SlackClient
import config
import re

# loggbot's ID as an environment variable
BOT_ID = config.BOT_ID


# constants
AT_BOT = "<@" + BOT_ID + ">"

slack_client = SlackClient(config.SLACK_ID)


def append_to_json(text, channel, user):
    date = time.strftime("%c")
    import json
    a_dict = {"user": user, "date": date, "text": text}

    data = []
    try:
        with open('logs/' + channel + '.json') as f:
            data = json.load(f)
    except IOError:
        pass

    data.append(a_dict)

    with open('logs/' + channel + '.json', 'w') as f:
        json.dump(data, f)

def replace_usernames(line):
    regex=re.compile(r"<+@+[\w\.-]+>")
    occurences=regex.findall(line)
    for user in occurences:
        try:
            user_info = slack_client.api_call("users.info", user=user.replace("<@","").replace(">","")) #so lazy
            line=line.replace(user, "@"+user_info['user']['name'])
        except:
            print("user not found")

    return line

def handle_command(command, channel, user, ts):
    """
    Receives commands directed at the bot and determines if they
    are valid commands. If so, then acts on the commands.
    Retrieves some more info from the API if needed.
    """

    # Help menu
    if command == "?":
        web_url = config.WEB_URL
        if web_url == "":
            web_url = "Not set in config"
            print(" * Warning: Web URL not set in config.")

        # Alright, so we need some kind of a help menu or something.
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Uhm.. Hei! Okei, dette er enkelt. Alt du trenger gjore er: Tagg meg (@logg) med "
                                   "noe du vil legge i loggen. \n\nF.eks. slik: '@logg Opprettet nye tilganger til "
                                   "Jens fra nedi gata, det var enkelt.'. \nKanskje litt annereledes, men du "
                                   "skjonner tegninga da! \n\nEtterhvert som man logger ting kan loggene leses i "
                                   "nettleseren din her: \n{0}. \n\nLykke til!".format(web_url),
                              as_user=True)

    else:
        slack_client.api_call("reactions.add", channel=channel, name="thinking_face", timestamp=ts, as_user=True)

        # Create the log stuff
        channel_info = slack_client.api_call("channels.info", channel=channel)
        user_info = slack_client.api_call("users.info", user=user)

        try:
            channel_name = channel_info['channel']['name']
        except:
            private_info = slack_client.api_call("groups.info", channel=channel)
            try:
                channel_name = private_info['group']['name']
            except:
                channel_name = channel

        try:
            user_nick = user_info['user']['name']
        except:
            user_nick = user

        try:
            real_name = user_info['user']['profile']['real_name']

        except:
            real_name = None

        if real_name is not None:
            user_nick = real_name + " (" + user_nick + ")"

        append_to_json(replace_usernames(command), channel_name, user_nick)

        # React to the post with the log stuff.
        slack_client.api_call("reactions.add", channel=channel, name="memo", timestamp=ts, as_user=True)
        slack_client.api_call("reactions.remove", channel=channel, name="thinking_face", timestamp=ts, as_user=True)


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
                try:
                    return output['text'].split(AT_BOT)[1].strip(), \
                           output['channel'], \
                           output['user'], \
                           output['ts']
                except:
                    # Magical thing we fixed via mobile ssh at the crewparty. Needs to be here aswell.
                    print("[ERROR] Failed to return slack output from function due to invalid response.")
    return None, None, None, None


def start_bot():
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
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
    print("Trying to stop thread")
    if self.process is not None:
        self.process.terminate()
        self.process = None

start_bot()
