from bot.events import command

import requests
import pprint
import json
import praw
import os.path

def __initialise__(server):
    if os.path.exists(server.get_config_dir("info.json")):
        infofile = server.get_config_dir("info.json")
    else:
        with open(server.get_config_dir("info.json"), "w") as f:
            f.write("{}")

@command("fcset", "(.+)")
def setinfo(server, message, text):
    ds = json.load(open(server.get_config_dir("info.json")))
    ds[server.lower(message.address.nick)] = text
    json.dump(ds, open(server.get_config_dir("info.json"), "w"))
    return "%s: Saved your info!" % message.address.nick

@command("fcget", r"(\S*)")
def getinfo(server, message, username):
    try:
        user = r.get_redditor(username)
    except requests.exceptions.HTTPError:
        return "Sorry, that is not a valid reddit user."
    for comment in user.get_comments():
        print(comment.subreddit)
        if str(comment.subreddit) == "pokemontrades" or str(comment.subreddit).lower() == "svexchange":
            comment_json = requests.get(comment.permalink + ".json", headers={"User-Agent": "/u/KnightHawk3's IRC bot called Rhythm"}).json()
            return str(comment_json[1]["data"]["children"][0]["data"]["author_flair_text"])

r = praw.Reddit("/u/KnightHawk3's IRC bot called Rhythm")

__callbacks__ = {"privmsg": [setinfo, getinfo]}
