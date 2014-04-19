import requests

from bot.events import command
from util.text import aligntable

@command("tsv", r"(\d{1,4})")
def get_tsv_thread(server, message, text):
    """
    - Syntax: [!@]tsv ^C03query^C
    - Description: Search /r/svexchange for a tsv
    """
    url = "http://www.reddit.com/r/SVExchange/search.json?q=flair%3Ashiny+AND+title%3A" + text + "&restrict_sr=on&sort=new&t=all"
    results = requests.get(url, headers={'User-Agent':'Rythm the IRC bot by /u/KnightHawk3 (melody)'}).json()
    tableresults = []
    
    for number, result in enumerate(results["data"]["children"]):
        line = ["\x0f"+result["data"]["title"], "http://redd.it/" + result["data"]["url"].split("/")[-3]]
        tableresults.append(line)
    table = aligntable(tableresults)

    for line in table:
        yield line

__callbacks__ = {"privmsg": [get_tsv_thread]}
