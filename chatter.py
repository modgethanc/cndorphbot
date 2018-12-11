#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A chatter engine for speech simulation.
"""

import random

vocab = {
        "friend": [
            "friend",
            "pal",
            "townie"
            ],
        "sleep": [
            "see you later, space cowboy",
            "taking a little breather",
            "i'll be back, i think"
            ],
        "greet": [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening"
            ],
        "positive": [
            "sweet",
            "rad",
            "cool",
            "neat",
            "awesome",
            "nice",
            "wow",
            "yeah",
            "yay"
            ],
        "no answer": [
            "not sure what you meant by that...",
            "sorry, i don't know what that means...",
            "i'm not that good at understanding you right now...",
            "i'm confused by what you said...",
            "that's not something i can figure out...",
            "you might want to check with someone else...",
            "i dunno how to handle this...",
            "i'll do my best",
            "umm...",
            "maybe ask someone else?",
            "i'm not the best one to talk to about this",
            "i'm trying!",
            "well, i dunno"
            ],
        "adjective": [
            "blue",
            "red",
            "vibrating",
            "dull",
            "round",
            "sandy",
            "invisible",
            "multicolor",
            "cold",
            "tepid",
            "soft",
            "lost",
            "favored",
            "bland",
            "heavy",
            "gentle",
            "orange",
            "dry",
            "floating",
            "backwards",
            "sly",
            "flippant"
            ],
        "stuff": [
            "pebble",
            "lid",
            "thought",
            "sock",
            "book",
            "footstool",
            "hi-five",
            "sticker",
            "iguana",
            "button",
            "bicycle",
            "flowerpot",
            "sack",
            "egg",
            "toadstool"
            ],
        "affection": [
            "aww, thanks <3",
            "thank you :)",
            "i appreciate it! :D",
            "yeee n_n",
            "heck yes <3",
            "ty :3"
            ],
        "cheer": [
            "cheer up, friend, it can't be so bad",
            "hey, don't worry about it",
            "it's cool, we'll work it out somehow",
            "hang in there, this'll pass",
            "i'm gonna do my best, okay?"
            ],
        "affirm": [
            "sure",
            "okay",
            "right",
            "yeah",
            "yep",
            "fine",
            "alright"
            ]
        }

def say(keyword):
  if keyword is "np":
    return random.choice([
        "my pleasure, "+say("friend"),
        "sure thing, "+say("friend"),
        "whatever, no biggie",
        "all cool",
        "yep"])
  else:
      return random.choice(vocab.get(keyword, ["i'm confused :("]))
