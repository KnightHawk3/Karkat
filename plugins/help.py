from bot.events import command

@command("help", "()")
def gethelp(server, message, text):
    return "http://bit.ly/1sR9c7j"

__callbacks__ = {"privmsg": [gethelp]}
