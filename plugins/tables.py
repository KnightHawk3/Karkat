from util.irc import command

@command("(╯°□°)╯︵ ┻━┻", r"(\S*)", public="")
def unflip(server, message, text):
    return "┬─┬﻿ ノ( ゜-゜ノ)"

__callbacks__ = {"privmsg": [unflip]}
