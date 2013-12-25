import re
import urllib.parse as urllib

import requests

from util.irc import Callback, command
from util.text import unescape

templates = {"@": "%(color).2d│ 02%(title)s\n%(color).2d│ 03↗ %(url)s\n%(color).2d│ %(description)s",
             ".": "%(color).2d│ %(title)s 12↗ %(url)s",
             "!": "%(color).2d│ %(title)s 12↗ %(url)s"}

maxlines = {"@": 1,
            ".": 4,
            "!": 6}
deflines = {"@": 1,
            ".": 1,
            "!": 4}


def google(query, nresults, retry={}):
    page = requests.get("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % urllib.quote(query)).json()

    if page["responseData"]["results"]:
        for keyword in retry:
            if any(keyword in i["title"].lower() for i in page["responseData"]["results"]):
                return google(retry[keyword], nresults)

        for i, result in enumerate(page["responseData"]["results"]): 
            if i >= nresults: return
            yield {"color" : [12, 5, 8, 3][i % 4],
                    "title" : unescape(re.sub("</?b>", "", result["title"])),
                    "url"   : result["unescapedUrl"],
                    "description": re.sub(r"\s+", 
                                          " ", 
                                          unescape(re.sub("</?b>", "", result["content"])))}

@Callback.threadsafe
@command(["google", "search"], "(-\d\s+)?(.+)", private="!", public=".@",
            usage="12Google│ Usage: !google [-NUM_RESULTS] <query>",
            error="04Google│ Error: Could not fetch google results.")
def google_template(server, message, nresults, query):
    if nresults:
        nresults = min(-int(nresults.strip()), maxlines[message.prefix])
    else:
        nresults = deflines[message.prefix]

    for data in google(query, nresults, {"suicide": "it gets better"}):
        yield templates[message.prefix] % data
    else:
        yield "05Google│ No results found."


__callbacks__  = {"privmsg": [google_template]}