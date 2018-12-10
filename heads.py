#!/usr/bin/python
"""
Framework for hooking up bot behavior with some frontend. Currently, only IRC protocol is supported.
"""

import os
import sys
import random
import re
import time
import importlib
import imp
import socket

import ircformatter
import chatter
import cndorphbot

class IRCMouth():
    """
    IRC Handler; works with oragano at the moment, and probably charybdis.

    """

    def __init__(self):
        ## misc constants

        self.IRCCONF = os.path.join("data", "config", "irc.conf")

        ## irc data

        self.BOTNAME = ""
        self.ADMIN   = ""
        self.SERVER = ""
        self.DEFAULTCHANS = []

        self.CHANNELS = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.arrest = False
        self.load()

    ## structural functions

    def load(self):
        '''
        Parse config file.

        Expected format:
        IRC.SERVERNAME.NET
        #DEFAULTCHAN,#DEFAULTCHAN2,#DEFAULTCHAN3
        BOTNAME
        ADMINNAME
        '''

        configfile = open(self.IRCCONF, "r")
        config = []
        for x in configfile:
            config.append(x.rstrip())
        configfile.close()

        self.BOTNAME = config[2]
        cndorphbot.set_nick(self.BOTNAME)
        self.ADMIN  = config[3]
        cndorphbot.set_admin(self.ADMIN)
        self.SERVER = config[0]
        self.DEFAULTCHANS = config[1].split(',')
        cndorphbot.set_home(self.DEFAULTCHANS[0])

        self.MAINCHAN = self.DEFAULTCHANS[0]

    def start(self):
        '''
        Connects and starts listening.
        '''

        self.load()
        self.connect(self.SERVER, self.DEFAULTCHANS, self.BOTNAME)

    def reload(self):
        '''
        Call reload on all loaded modules.
        '''

        importlib.reload(self.ircformatter)
        self.listen()

    ### irc functions

    def send(self, msg):
        '''
        Wraps the message by encoding it to bytes, then sends it to current
        socket.
        '''

        print("> " + msg)
        self.sock.send(msg.encode('utf-8'))

    def ping(self, pingcode):
        '''
        Pongs the server.
        '''

        self.send("PONG :"+pingcode+"\n")

        response = cndorphbot.ping()
        self.multisay(self.MAINCHAN, response)

    def joinchan(self, chan):
        '''
        Joins named channel, and adds it to global channel list.
        '''

        self.CHANNELS.append(chan)
        self.send("JOIN "+ chan +"\n")
        print(self.CHANNELS)

    def part(self, chan):
        '''
        Leaves named channel, and removes it from the global channel list.
        '''

        print(self.CHANNELS)
        self.CHANNELS.remove(chan)
        self.send("PART "+ chan +" :"+chatter.say("sleep")+"\n")

    def connect(self, server, channel, botnick):
        '''
        Connects to server, naming itself and owner, and automatically joins list
        of channels.
        '''

        self.sock.connect((server, 6667))
        self.send("USER "+botnick+" "+botnick+" "+botnick+" :"+self.ADMIN+"'s bot\n")
        self.send("NICK "+botnick+"\n")

        while 1:
            # wait for mode set before joining channels
            msg = self.sock.recv(2048).rstrip()

            if msg:
                print("< " + msg)

                if msg.find("PING :") == 0:
                    pingcode = msg.split(":")[1]
                    self.ping(pingcode)

                elif msg.find("MODE") != -1:

                    for chan in self.DEFAULTCHANS:
                        self.joinchan(chan)
                    return

                elif msg.find("ERROR") == 0:
                    print("connection error :(")
                    return

    def disconnect(self):
        '''
        Disconnects from server.
        '''

        self.send("QUIT " +chatter.say("sleep") + "\n")
        self.sock.close()

    def say(self, channel, msg, nick=""):
        '''
        Sends message to single channel, with optional nick addressing, and no
        delay.
        '''

        #if nick == channel: #don't repeat nick if in PM
        #  nick = ""
        #elif nick:
        #  nick += ": "

        # TODO: This strips nick addressing altogether, since I can't figure
        # out how to do this consistently. Offloading nick addressing to the
        # bot core for now.

        nick = ""

        self.send("PRIVMSG "+channel+" :"+nick+msg+"\n")

    def multisay(self, channel, msglist, nick=""):
        '''
        Takes a list of messages to send and sends them.

        Also provides the option of processing a dict from an individual
        message, extracting "msg" and "channel" appropriately.
        '''

        for line in msglist:
            msg = ""
            chan_target = ""
            nick_target = ""

            if isinstance(line, dict):
                # message metadata handling

                msg = line.get("msg", "")
                chan_target = line.get("channel", "")
                nick_target = line.get("nick", "")

                if chan_target:
                    if chan_target == "MAIN":
                        channel = self.MAINCHAN
                    else:
                        channel = chan_target

                if not nick_target:
                    nick = ""
                else:
                    nick = str(nick_target)
            else:
                msg = line

            self.say(channel, msg, nick)

    def wall(self, msg, nick=""):
        '''
        Sends a single message to all CHANNELS with simulated typing speed, and
        optional nick addressing.
        '''

        for x in self.CHANNELS:
            self.say(x, msg, nick)

    def multiwall(self, msglist, nick=""):
        '''
        Takes a list of messages to send, and sends them to all channels
        with simulated typing speed, nd optional nick addressing.
        '''
        for x in msglist:
            self.wall(x, nick)

    def is_pm(self, parsed):
        '''
        Checks if parsed message is a PM.
        '''
        return parsed.get("channel") == parsed.get("nick")

    def admin_panel(self, channel, user, time, msg):
        '''
        Various admin-only commands.
        '''

        if msg.find("!join") == 0:
            self.say(channel, "k", user)
            split = msg.split(" ")
            for x in split:
                if x.find("#") != -1:
                    self.joinchan(x)
                    return "join"

        elif msg.find("!brb") == 0:
            self.say(channel, chatter.say("sleep"), user)
            self.part(channel)
            return "part"

        elif msg.find("!quit") == 0:
            self.say(channel, chatter.say("sleep"), user)
            self.disconnect()
            return "die"

        elif msg.find("!names") == 0:
            self.send("NAMES "+channel+"\n")
            return "names"

        elif msg.find("!channels") == 0:
            chanlist = " ".join(self.CHANNELS)
            self.say(channel, "i'm in "+chanlist)
            return "names"

        elif msg.find("!wall") == 0:
            split = msg.split("!wall ")
            wallmsg = "".join(split[1])
            self.wall(wallmsg)
            return "wall"

        elif msg.find("!say") == 0:
            splitter = msg.split("!say ")[1]
            parse = splitter.split(" ")
            self.say(parse[0], " ".join(parse[1:]))
            return "say"
        else:
            self.multisay(channel, cndorphbot.admin_panel(channel, user, time, msg))

    def listen(self):
        '''
        A loop for listening for messages.
        '''

        while 1:
            msg = self.sock.recv(2048)
            if msg:
                try:
                    msgs = msg.split("\n")
                    for line in msgs:
                        self.handle(line.decode('utf-8'))
                except UnicodeDecodeError:
                    continue

    def handle(self, msg):
        '''
        Main message handler. Reponds to ping if server pings; otherwise,
        parses incoming message and handles it appropriately.

        If the message was a PM, responds in that PM.

        If the message was from the bot owner, call admin_panel() before
        proceeding.
        '''

        msg = msg.strip('\n\r')

        print("< "+msg)

        if re.match("^PING", msg):
            return self.ping("pong")

        msg = msg.strip('\n\r')
        parsed = ircformatter.parse_dict(msg)

        ## actions on join
        if parsed.get("command") == "JOIN":
            self.multisay(
                    parsed.get("channel"),
                    cndorphbot.seen(parsed.get("channel"), parsed.get("nick")),
                    parsed.get("nick")
                    )

        if parsed.get("command") == "MODE":
            if re.match("\+o "+self.BOTNAME, parsed.get("message")):
                self.say(parsed.get("channel"), chatter.say("affection"))

        ## actions on ACTION
        if len(parsed.get("message", "").split("ACTION")) > 1:
            response = cndorphbot.did(
                    parsed.get("channel"),
                    parsed.get("nick"),
                    " ".join(parsed.get("message").split("ACTION ")[1:])
                    )
            if len(response) > 0:
                self.multisay(
                        parsed.get("channel"),
                        response,
                        parsed.get("nick")
                        )

        ## actions on privmsg
        if parsed.get("command") == "PRIVMSG":
            ## if this is a PM, switch channel for outgoing message
            if parsed.get("channel") == self.BOTNAME:
                parsed.update({"channel":parsed.get("nick")})

            ## catch admin command
            if parsed.get("nick") == self.ADMIN:
                code = self.admin_panel(parsed.get("channel"), parsed.get("nick"), parsed.get("time"), parsed.get("message"))
                if code:
                   return

            if parsed.get("message").find(self.BOTNAME+": ") != -1 or self.is_pm(parsed):
                # put stuff here for direct address
                self.multisay(
                        parsed.get("channel"),
                        cndorphbot.addressed(parsed.get("channel"), parsed.get("nick"), parsed.get("time"), parsed.get("message")),
                        parsed.get("nick")
                        )
            else:
                # general responses
                self.multisay(parsed.get("channel"), cndorphbot.said(parsed.get("channel"), parsed.get("nick"), parsed.get("time"), parsed.get("message")), random.choice([parsed.get("nick"), ""]))

        sys.stdout.flush()
