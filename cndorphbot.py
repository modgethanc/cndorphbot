#!/usr/bin/python
"""
Main core behavior and data management.
"""

import os
import sys
import random
import re
import time

import inflect

import chatter
import utils

### globals

DATA_DIR = "data"
HOME_CHAN = "#test"
SELF = {}
TOWNIES = {}

BOTNICK = "cndorphbot"
ADMIN = ""

### config
p = inflect.engine()

### setup

def load_self():

    global SELF

    filename = os.path.join(DATA_DIR, "self.json")
    if not os.path.exists(filename):
        SELF = {}

    SELF = utils.open_json_as_dict(filename)

    return filename

def save_self():
    filename = os.path.join(DATA_DIR, "self.json")
    utils.write_dict_as_json(filename, SELF)

    return filename

def set_home(new_home):
    """
    Changes home channel.
    """

    global HOME_CHAN
    HOME_CHAN = new_home

def set_nick(new_nick):
    '''
    Changes name.
    '''

    global BOTNICK
    BOTNICK = new_nick

def set_admin(new_admin):
    """
    Sets the admin nick.
    """

    global ADMIN
    ADMIN = new_admin

def load_townies():
    """
    Loads all townies from data directory, returning a list of townie nicks.
    """

    global TOWNIES

    for filename in os.listdir(DATA_DIR):
        entry = os.path.basename(filename).split(".")

        if not entry[0] or len(entry) < 2:
            continue
        if entry[1] == "townie":
           incoming = Townie(entry[0])
           TOWNIES.update({incoming.load(entry[0]):incoming})
           print(incoming.to_string(False))

    return TOWNIES.keys()

def townie_check(nick):
    """
    Checks if the nick is in current townie registry; create a new townie if not!
    """

    global TOWNIES

    if not nick in TOWNIES:
        townie = Townie(nick)
        townie.save()
        TOWNIES.update({nick: townie})

### irc fuctions

def said(channel, user, now, msg, network="", addressed=False):
    """
    Response to something said in a channel, when not directly addressed.
    """

    global haunting
    global hauntChannel

    response = []
    townie_check(user)
    dice = random.randrange(0, 100)
    print(dice)
    absorb(msg)

    ## commands

    if re.match("^!rollcall", msg) or re.match("^!help", msg):
        response.append("cndorphbot here! i'm pretty useless, but i'm doing my best. i know about: !conjure, !botsnack, !snack-count. send a pm to {admin} if you think i'm misbehaving!".format(admin=ADMIN))
    if re.match("^!conjure", msg):
        time.sleep(random.randrange(2,5))
        response.append(conjure_handler(user))
    elif re.match('^!botsnack', msg):
        response.append(botsnack_handler(user))
    elif re.match('^!snack-count', msg):
        response.append("i have {snacks}!".format(snacks=p.no("snack", SELF.get("botsnacks", 0))))
    elif re.match('^!tricks', msg):
        response.append("i've learned the following tricks: "+", ".join(SELF.get("tricks", [])))
    else:
        ## passive random behavior
        if dice > 95:
            response.append(trick())

    return response

def addressed(channel, user, now, msg, network=""):
    """
    Responses when directly addressed. Assumes addressed before being called.
    Does a check for townie record.
    """

    global SELF

    response = []
    responding = True
    townie_check(user)
    if channel != BOTNICK:
        tag = user + ": "
    else:
        tag = ""

    if msg.find("botsnack") != -1:
        time.sleep(2)
        response.append(botsnack_handler(user))
    elif msg.find("time") != -1:
        response.append(tag+str(now))
    elif msg.find("<3") != -1:
        time.sleep(1)
        response.append(tag+":)")
    elif msg.find("sync") != -1:
        response.append(tag+str(SELF.get("mark", 0)))
    elif msg.find("mark") != -1:
        SELF.update({"mark": now})
        save_self()
        response.append(tag+"sync! ({time})".format(time=now))
    elif msg.find(":(") != -1:
        time.sleep(2)
        response.append(tag+chatter.say("cheer"))
    elif msg.find(":)") != -1:
        time.sleep(2)
        response.append(tag+":D")
    elif msg.find("report") != -1:
        response.append("!tildescore")
    else:
        if user == "tildebot":
            response.append({
                "channel": ADMIN,
                "msg": msg
                })
        else:
            time.sleep(3)
            response.append(tag+chatter.say("no answer"))

    return response

def seen(channel, user):
    """
    Handler for processing join actions.
    """

    time.sleep(random.randrange(2,4))

    response = []
    msg = ""

    if user == BOTNICK:
        print("joined "+channel)
        msg = "{greet}, {townies}!".format(greet=chatter.say("greet"),
                townies=p.plural(chatter.say("friend")))
    else:
        townie_check(user)

    if msg:
        response.append(msg)
    return response

def did(channel, user, msg):
    """
    Responders to ACTIONs.
    """

    response = []
    global SELF

    if user == "kelpiebot":
        ## handler for ,get response
        if msg.startswith("retrieves"):
            if msg.find("hands it to "+BOTNICK) != -1:
                item = " ".join(msg.split("retrieves ")[1:]).split(" and hands it to")[0].split(" ")[1:]
                item[0] = item[0][1:]
                item[-1] = item[-1][:-1]

                thing = " ".join(item)
                inv = SELF.get("inv", [])
                inv.append(thing)
                SELF.update({"inv": inv})
                print("got "+thing)
                save_self()

                response.append("{sweet}! thanks for the {thing}!".format(sweet=chatter.say("positive"), thing=thing))

    return response

def admin_panel(channel, nick, now, msg):
    """
    Actions only the admin may request.
    """

    response = []

    if nick != ADMIN:
        return response

    return response

def ping():
    """
    Actions on getting a server ping.
    """

    response = []

    dice = random.randrange(0, 100)

    ## always report ping to ADMIN; this keeps the irc handler happy, at the
    ## cost of being extremely noisy for ADMIN
    response.append({
        "msg": "i got a ping! ({dice})".format(dice=dice),
        "channel": ADMIN
        })

    if dice > 90 and dice < 95:
        response.append({
            "msg": trick(),
            "channel": "MAIN"
            })

    return response

## misc handlers

def trick():
    """
    Pull a random command and return it. If no commands learned, just smile
    vacantly.
    """
    trick = random.choice(SELF.get("tricks", [":)"]))
    if trick in ["!water", "!talklike"]:
        ## manual targetted tricks
        trick = "{trick} {target}".format(trick=trick, target=random.choice(TOWNIES.keys()))
    if trick in ["!wiki-philosophy"]:
        trick = "{trick} {target}".format(trick=trick, target=chatter.say("stuff"))

    return trick

def absorb(msg):
    """
    Take apart {msg} for things that ought to be absorbed.
    """

    global SELF

    tokens = msg.split(" ")
    for token in tokens:
        if token.startswith("!") and\
           token not in SELF.get("tricks", []) and\
           token not in SELF.get("commands", []):
            ## learn !incantations
            tricks = SELF.get("tricks", [])
            tricks.append(token.split(",")[0].split(".")[0])
            SELF.update({"tricks": tricks})
            save_self()

    return

def conjure_handler(nick):
    """
    Generats a mysterious item and gives it to the named person.
    """
    global SELF

    thing = "{adjective} {stuff}".format(adjective=chatter.say("adjective"), stuff=chatter.say("stuff"))
    count = TOWNIES.get(nick).give_item(thing)

    return "here, take this {thing}! you've got {things} from me now.".format(thing=thing,
            things=p.no("thing", count))

def botsnack_handler(nick):
    """
    Increments own botsnack received count, and botsnack given count for
    {nick}; returns an affectionate phrase.
    """
    global SELF

    TOWNIES.get(nick).give_botsnack()
    count = SELF.get("botsnacks", 0)
    count += 1
    SELF.update({"botsnacks": count})
    save_self()

    return "{nick}: {affection}".format(nick=nick, affection=chatter.say("affection"))

## CLASSES

class Townie():
    """
    Data management for individual irc users.
    """

    def __init__ (self, nick=""):
        """
        Starting info.
        """

        self.nick = nick
        self.aliases = []
        self.snacksGiven = 0
        self.inventory = []

    def save(self):
        '''
        Write self to disk.
        '''

        filename = os.path.join(DATA_DIR, self.nick+".townie")
        utils.write_dict_as_json(filename, self.to_dict())

        return filename

    def to_dict(self):
        """
        Turns all data into a dict.
        """

        return {
                "nick": self.nick,
                "aliases": self.aliases,
                "snacksGiven": self.snacksGiven,
                "inventory": self.inventory
                }

    def to_string(self, oneline=True):
        """
        String representation of this townie.
        """

        if len(self.aliases) < 2:
            aliases = "no other known aliases"
        else:
            aliases = ", ".join(self.aliases)

        if oneline:
            return """a {townie} named {nick}, who also goes by {aliases}""".format(
                    townie=chatter.say("friend"),
                    nick=self.nick,
                    aliases=aliases,
                    )
        else:
            return """\
    a {townie} named {nick} who has given me {botsnacks}""".format(
                    townie=chatter.say("friend"),
                    nick=self.nick,
                    botsnacks=p.no("botsnack", self.snacksGiven)
                    )

    def load(self, townie_name):
        """
        Loads named townie from datafile into self.
        """

        filename = os.path.join(DATA_DIR, townie_name + ".townie")

        if not os.path.exists(filename):
            return False

        townie_data = utils.open_json_as_dict(filename)
        self.nick = townie_data.get("nick", "")
        self.aliases = townie_data.get("aliases", [])
        self.snacksGiven = townie_data.get("snacksGiven", 0)
        self.inventory = townie_data.get("inventory", [])

        return self.nick

    ## actions

    def give_botsnack(self):
        """
        Increments botsnack count.
        """

        self.snacksGiven += 1
        self.save()

    def give_item(self, item):
        """
        Adds item to inventory, returning number of items.
        """

        self.inventory.append(item)
        return len(self.inventory)


## default actions

print("""
 _______________________________________
|                                       |
|  C N D O R P H      C O N S O L E     |
|                                       |
|  yo pal what's up                     |
|_______________________________________|

i'm {botnick}
here's what we got:
""".format(botnick=BOTNICK))
load_self()
load_townies()

print("""
[ awaiting orders ... ]
""")
