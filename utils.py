#!/usr/bin/python
"""
Misc utility functions.
"""


import inflect
import time
import random
import os
import json

p = inflect.engine()

def input_yn(query):
    '''
    given a query, returns boolean True or False by processing y/n input.
    repeatedly queries until valid 'y' or 'n' is entered.
    '''

    try:
        ans = raw_input(query+" [y/n] ")
    except KeyboardInterrupt:
        input_yn(query)

    while ans not in ["y", "n"]:
        ans = raw_input("'y' or 'n' please: ")

    if ans == "y":
        return True
    else:
        return False

def pretty_time(time):
    '''
    human-friendly time formatter.

    takes an integer number of seconds and returns a phrase that describes it,
    using the largest possible figure, rounded down (ie, time=604 returns '10
    minutes', not '10 minutes, 4 seconds' or '604 seconds')
    '''

    m, s = divmod(time, 60)
    if m > 0:
        h, m = divmod(m, 60)
        if h > 0:
            d, h = divmod(h, 24)
            if d > 0:
                w, d = divmod(d, 7)
                if w > 0:
                    mo, w = divmod(w, 4)
                    if mo > 0:
                        return p.no("month", mo)
                    else:
                        return p.no("week", w)
                else:
                    return p.no("day", d)
            else:
                return p.no("hour", h)
        else:
            return p.no("minute", m)
    else:
        return p.no("second", s)

def genID(digits=5):
    '''
    returns a string-friendly string of digits, which can start with 0.
    defaults to 5 digits if length not specified.
    '''

    id = ""
    x  = 0
    while x < digits:
        id += str(random.randint(0,9))
        x += 1

    return id

def open_json_as_dict(filename):
    '''
    Opens filename.json file and returns dict (blank if no file)
    '''

    if not os.path.isfile(filename):
        return {}
    else:
        return json.load(open(filename))

def write_dict_as_json(filename, j):
    '''
    Overwrites filename.json file with dict j
    '''

    datafile = open(filename, 'w')
    datafile.write(json.dumps(j, sort_keys=True, indent=2, separators=(',', ':')))

    return filename
