#!/usr/bin/python
from web import Web
from bot import Bot

import threading, time
from threading import Thread

global shutdown_server
global stop_bot


def start_web():
    print ' ## Starting web thread'
    webClass = Web()
    webClass.startWeb()


def start_bot():
    print ' ## Starting bot thread'
    bot_class = Bot()
    bot_class.startBot()


if __name__ == '__main__':

    t1 = Thread(target=start_bot)
    t2 = Thread(target=start_web)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print(" ## Thank you and welcome back to Logger Bot for Slack!")
