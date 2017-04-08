#!/usr/bin/python
from web import Web
from bot import Bot

import threading, time
from threading import Thread

class loggerbot:

    global shutdown_server
    global stop_bot

    def startweb():
        print ' ## Starting web thread'
        webClass = Web()
        webClass.startWeb()

    def startbot():
        print ' ## Starting bot thread'
        botClass = Bot()
        botClass.startBot()

    if __name__ == '__main__':

        t1 = Thread(target = startbot)
        t2 = Thread(target = startweb)
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()

        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print(" ## Thank you and welcome back to Logger Bot for Slack!")
