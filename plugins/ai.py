import os
import re
import random
import requests
import time
import json
import math

from bot.events import Callback, command, msghandler
from util.irc import Message
from util.text import ircstrip

def sigmoid(x):
    return 2 / (1 + math.e**(-x)) - 1


class Mutators(object):
    @staticmethod
    def cobed(line, weights):
        print("Cobedising. In: %s" % line)
        line = requests.get("http://cobed.gefjun.rfw.name/", params={"q": ircstrip(line.lower())}, headers={"X-Cobed-Auth": "kobun:nowbunbun"}).text.upper()
        print("           Out: %s" % line)
        line = re.sub(r"^\S+:\s*", "", line)
        weights["cobedise"] += 1
        return line

class AI(Callback):
    learningrate = 0.01
    laughter = {"lol": 1, "lmao": 1, "rofl": 1, "ha": 0.5, "lmfao": 1.5}
    positive = "amazing woah cool nice sweet awesome yay ++ good great true yep <3 :D impressive".split()
    negative = "lame boring what ? uh why wtf confuse terrible awful -- wrong nope sucks".split()
    coeff = "wow fucking ur really !".split()

    def __init__(self, server):
        self.configdir = server.get_config_dir("AI")
        if not os.path.exists(self.configdir):
            os.makedirs(self.configdir, exist_ok=True)
        try:
            self.lines = open(self.configdir + "/caps.txt").read().split("\n")
        except FileNotFoundError:
            self.lines = ["HELLO"]
        self.server = server
        super().__init__(server)

        try:
            self.settings = json.load(open(self.configdir + "/settings.json"))
        except:
            self.settings = {
                "construct": 0.314159265359,                             # pi/10
                "lower": 0.115572734979,                                 # pi/10e
                "correction": 0.66180339887498948,                       # (1 + sqrt(5)) / 20 + 0.5
                "tangent": 0.164493406685,                               # pi^2 / 6
                "wadsworth": 0.20322401432901574,                            # sqrt(413)/100
                "wadsworthconst": 0.3,
                "cobedise": 0.0429,                                      # Kobun's filth ratio
                "suggest": 0,                                            # not implemented and this is a terrible idea
                "grammerify": 0,                                         # not implemented and also a terrible idea
                "internet": 90.01,                                       # what does this even mean
                "sentience": 0.32,                                       # oh god oh god oh god
            }

        try:
            self.istats = json.load(open(self.configdir + "/inputs.json"))
        except:
            self.istats = {}

        self.last = ""
        self.lasttime = 0
        self.lastmsg = ""
        self.context = []
        self.trigger_rate = 0.3

        self.lastlines = []


    def continuity(self, words, retain):
        # Boost probability of common words being used as the seed
        self.context.extend(list(set(self.last.upper().split()) & set(words)) + self.last.split())
        if "\x01ACTION" in words:
            self.context.extend("\x01ACTION") # Increase probability of repeated actions in context
        random.shuffle(self.context)
        # Calculate # of words to keep
        retain = int(len(self.context) * retain * 1.15)
        self.context = self.context[:retain]
        # Add all words from prior text
        text = words + list(self.context)
        return text
        

    def getline(self, sender, text):
        weights = {i: 0 for i in self.settings}
        inputs = []

        words = text.upper().split()

        words = self.continuity(words, random.random())

        choices = [i for i in self.lines if random.choice(words).lower() in i.lower() and i.lower().strip() != text.lower().strip()]
        if len(choices) < random.choice([2,3]):
            choices = []
            for i in range(random.randrange(3,9)):
                choices.append(random.choice(tuple(self.lines)))
        answer = random.choice(choices)
        inputs.append(answer)

        self.last = answer

        if choices[1:] and random.random() < self.settings["construct"]:
            common = set()
            stuff = set(choices)
            stuff.remove(answer)
            words = set()
            for i in stuff:
                words |= set([x.lower() for x in i.split()])
            common = set(answer.lower().split()) & words
            if common:
                word = list(common)[0]
                other = random.choice([i for i in stuff if word in i.lower().split()])
                inputs.extend(other)
                print(("Value constructed. Baseword: %r :: Seeds: %r & %r" % (word, answer, other)))
                answer = " ".join(answer.split()[:answer.lower().split().index(word)] + other.split()[other.lower().split().index(word):])
                # Using construct algorithm
                weights["construct"] += 1
        
        if random.random() < self.settings["wadsworth"] and answer[0] != "\x01":
            truncate = int(self.settings["wadsworthconst"] * len(answer))
            truncate, keep = answer[:truncate], answer[truncate:]
            answer = keep.lstrip() if keep.startswith(" ") else (truncate.split(" ")[-1] + keep).lstrip()
            print(("Wadsworthing. Throwing away %r, product is %r" % (truncate, answer)))
            # Using wadsworth algorithm
            weights["wadsworth"] += 1
        
        answer = answer.split(" ")
        
        if hasattr(self.server, "spellcheck") and random.random() < self.settings["correction"]:
            fixed = []
            for i in answer:
                correction = self.server.spellcheck(i.lower())
                fixed.append(i if not correction else correction[i.lower()][0])
            if " ".join(answer) != " ".join(fixed):
                print(("Spellchecked. Original phrase: %r ==> %r" % (" ".join(answer), " ".join(fixed))))
                answer = fixed
                # Using spellchecker algorithm
                weights["correction"] += 1
            
        if random.random() < self.settings["tangent"]:
            print(("Reprocessing data. Current state: %r" % (" ".join(answer))))
            answer, child_weights, child_inputs = self.getline(sender, " ".join(answer))
            answer = answer.split(" ")
            inputs.extend(child_inputs)
            # Using tangent algorithm
            weights = {k: v/2 + child_weights[k] for k, v in weights.items()}
            weights["tangent"] += 1
        
        rval = [sender if "".join(k for k in i if i.isalnum()).lower() in list(map(str.lower, self.server.nicks)) + ["binary", "disconcerted"] else (i.lower().replace("bot", random.choice(["human","person"])) if i.lower().find("bot") == 0 and (i.lower() == "bot" or i[3].lower() not in "ht") else i) for i in answer]
            
        rval = " ".join(rval).strip().upper().replace("BINARY", sender.upper())

        if random.random() < self.settings["cobedise"]:
            try:
                rval = Mutators.cobed(rval, weights)
            except:
                print("Cobed failed.")

        # Fix mismatching \x01s
        if rval[0] == "\x01" and rval[-1] != "\x01": 
            rval += "\x01"

        return rval, weights, inputs

    def addline(self, users, line):
        for i in users:
            line = re.sub(r"\b%s\b" % re.escape(i), "BINARY", line, flags=re.IGNORECASE)
        self.lines.append(re.sub(r"\b(rhythm|pipey|karkat|\|)\b", "BINARY", line, flags=re.IGNORECASE))
        with open(self.configdir + "/caps.txt", "w") as f:
            f.write("\n".join(self.lines))

    @Callback.background
    @msghandler
    def capsmsg(self, server, msg):
        if not (msg.text[0].isalpha() or msg.text[0] == "\x01"):
            return
        triggers = [msg.text.lower().startswith("%s:" % server.nick.lower()) or "rhythm" in msg.text.lower() or "!!!" in msg.text.lower() or "Rhythm" in msg.text]
        if any(triggers):
            self.trigger_rate = min(1, self.trigger_rate + 0.1 + 0.15 * (triggers[0]))
            if random.random() > self.trigger_rate:
                return
            response, weights, inputs = self.getline(msg.address.nick, msg.text.upper())
            yield response
            self.lasttime = time.time()
            self.lastmsg = response
            self.lastlines.append((time.time(), msg.context, weights, inputs, {}))
        else:
            self.trigger_rate = max(0.25, self.trigger_rate - 0.025)
        if triggers[0] and msg.text not in self.lines:
            self.addline(server.channels.get(server.lower(msg.context), [msg.context]), msg.text.upper())

    @command("purge", "(.*)", admin=True)
    def purge(self, server, message, query):
        start = len(self.lines)
        last = query or self.last
        self.lines = [i for i in self.lines if i.upper() != last.upper()]
        with open(self.configdir + "/caps.txt", "w") as f:
            f.write("\n".join(self.lines))
        return "Removed %d instance(s) of %r from shouts." % (start - len(self.lines), last)

    def score(self, text):
        msg = text.lower()
        # Positive reactions include:
        # Laughter
        score = 0
        for i in self.laughter:
            score += self.laughter[i] * msg.count(i)
        # Positivity
        for i in self.positive:
            score += msg.count(i)
        # Negativity
        for i in self.negative:
            score -= msg.count(i)

        # Activations:
        if msg.startswith("%s:" % self.server.nick.lower()) or (text.isupper() or "karkat" in msg or "pipey" in msg):
            score += 0.4
        else:
            score -= 0.025

        # Emotional aggravators
        coeff = 1
        for i in self.coeff:
            coeff += 0.3 * msg.count(i)
        return score * coeff

    def adjust_weights(self, server, line) -> "privmsg":
        msg = Message(line)
        score = self.score(msg.text)
        now = time.time()
        adjust = [i for i in self.lastlines if now - 60 >= i[0]]
        for t, channel, weights, inputs, adjustments in adjust:
            # Commit changes
            for k, v in adjustments.items():
                pass
                # self.settings[k] += sigmoid(v) * self.learningrate

        self.lastlines = [i for i in self.lastlines if now - 60 < i[0]]
        for t, channel, weights, inputs, adjustments in self.lastlines:
            if server.eq(channel, msg.context):
                c = score * (1 - (now - t) / 60)
                for k, v in weights.items():
                    adjustments.setdefault(k, 0)
                    adjustments[k] += c * v
                for i in inputs:
                    self.istats.setdefault(i, 1)
                    self.istats[i] += c * self.learningrate
        self.settings = {k: min(1, max(0, v)) for k, v in self.settings.items()}

        with open(self.configdir + "/settings.json", "w") as f:
            json.dump(self.settings, f)
        with open(self.configdir + "/inputs.json", "w") as f:
            json.dump(self.istats, f)

    def shh(self, server, line) -> "privmsg":
        if re.match("shh+", Message(line).text) and time.time() - self.lasttime < 30:
            msg = ""
            for i in self.lastmsg:
                if i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    msg += "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"[ord(i) - 65]
                else:
                    msg += i                    
            server.message(msg, Message(line).context)

__initialise__ = AI

