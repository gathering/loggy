#!/usr/bin/python

import time
from multiprocessing import Process

import bot
import web
import os
import glob
import shutil

def start_web():
    print (' ## Starting web thread')
    web.start_web()


def start_bot():
    print (' ## Starting bot thread')
    bot.start_bot()

if __name__ == '__main__':

    if (not os.path.isfile('users.json')):
        print (' * No users, creating initial users file')
        shutil.copy('example.users.json', 'users.json')

    if (not len(glob.glob(os.path.join('logs/*'))) > 0):
        print (' * No logs, creating initial general channel file')
        shutil.copy('example.channel.json', 'logs/general.json')

    t1 = Process(target=start_bot)
    t2 = Process(target=start_web)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print(" ## Thank you and welcome back to Logger Bot for Slack!")
