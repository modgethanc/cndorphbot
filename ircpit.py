#!/usr/bin/python
"""
Main launcher for an IRC bot.
"""

import heads
import imp
import utils

def start():
    bot = heads.IRCMouth()
    bot.start()
    run_bot(bot)

def run_bot(head):
    try:
        head.listen()
    except KeyboardInterrupt:
        print("")
        proceed = utils.input_yn("reload?")

        if proceed:
            heads.cndorphbot.save_self()
            s = head.sock
            chans = head.CHANNELS
            imp.reload(heads)
            imp.reload(heads.cndorphbot)
            imp.reload(heads.chatter)
            imp.reload(heads.cndorphbot.chatter)
            head = heads.IRCMouth()
            head.sock = s
            head.CHANNELS = chans
            run_bot(head)

if __name__ == "__main__":
    start()
