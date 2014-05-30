# clone of http://willyoupressthebutton.com/
# I make lots of obvious mistakes when I'm sleepy
# inb4 obvious mistakes

import sys
import json
import random
import math
import requests
import re
from util.text import unescape, lineify

from bot.events import Callback, command

class Wyp(Callback):
    QFILE = "wyps.json"

    def __init__(self, server):
        self.qfile = server.get_config_dir(self.QFILE)
        try:
            with open(self.qfile) as f:
                self.wyps = json.load(f)
        except:
            self.wyps = {}
        self.active = "04●"
        super().__init__(server)

    @command("addbutton makebutton addwyp makewyp", r"(.+)")
    def queue(self, server, msg, item):
        wyp = self.wyps.setdefault(item, {})
        self.active = item
        self.save()
        return "\x0306│\x03 Button added"

    @command("fuckbutton destroy ripbutton")
    def destroy(self, server, msg):
        item = self.active
        nick = msg.address.nick
        wyp = self.wyps.setdefault(item, {})
        wyp[server.lower(nick)] = None
        self.save()
        return "\x0306│\x03 You attack the button. " + self.displayPresses(item)        

    @command("whatton")
    def active(self, server, msg):
        return self.fancydisplay()

    @command("button wyptb wyp willyoupressthebutton willyoupress")
    def preview(self, server, msg):
        nick = msg.address.nick
        # Check if we need any new buttons
        if all(i for i in self.wyps.values()):
            page = requests.get("http://m.willyoupressthebutton.com/").text
            cond = unescape(re.findall('<div class="rect" id="cond">(.+)</div>', page)[0])
            res = unescape(re.findall('<div class="rect" id="res">(.+)</div>', page)[0])
            res = res[0].lower() + res[1:]
            wyp = self.wyps.setdefault("%s but %s" % (cond, res), {})
            self.save()
        # Reduce probability of already-answered buttons
        buttons = [i for i in self.wyps if server.lower(nick) not in self.wyps[i] or random.random() < 0.1]
        self.active = random.choice(buttons)
        return self.display()

    @command("press yes bonk boop touch")
    def press(self, server, msg):
        item = self.active
        nick = msg.address.nick
        wyp = self.wyps.setdefault(item, {})
        wyp[server.lower(nick)] = 1
        self.save()
        return "\x0306│\x03 You pressed the button. " + self.displayPresses(item)

    @command("nopress no")
    def noPress(self, server, msg):
        item = self.active
        nick = msg.address.nick
        wyp = self.wyps.setdefault(item, {})
        wyp[server.lower(nick)] = 0
        self.save()
        return "\x0306│\x03 You chose not to press the button. " + self.displayPresses(item)

    def displayPresses(self, item=None):
        if item is None:
            item = self.active
        wyp = self.wyps.get(item)
        num = len(wyp.keys())
        numPress = list(wyp.values()).count(1)
        stats = "%s out of %s people pressed the button (%.2f%%)" % (numPress, num, numPress / num * 100)
        health = 1
        if None in wyp.values():
            health -= 2 * list(wyp.values()).count(None) / self.average()
            if health < 0:
                del self.wyps[item]
                self.save()
                stats += ". The button has been destroyed. RIP, button."
            bar = list("  ʜᴇᴀʟᴛʜ  ")
            bar.insert(max(0, math.ceil(health * 10)), "15,14")
            stats += " 15,06%s" % "".join(bar)
        return stats
            

    def display(self, item=None):
        return "\x0306│\x03 Will you press the button? " + self.active

    def fancydisplay(self):
        button = """╔═══╕ %s
║ 04● │ %s
╙───┘ Will you press the button?"""
        k = 64
        while True:
            text = lineify(self.active, k)
            k += 8
            if len(text) < 3: break
        if len(text) == 1: text.append("")
        return button % tuple(text)

    def average(self):
        return sum(len(i.values()) for i in self.wyps.values()) / len(self.wyps)

    def save(self):
        with open(self.qfile, "w") as f:
            json.dump(self.wyps, f)


__initialise__ = Wyp

"""
╔═════╕
║ RIP │
║  04●  │
║ , .╷│
"""

╔═══╕
║ 04● │
╙───┘


