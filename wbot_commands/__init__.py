#! /usr/bin/python3
import wbot_commands.wiki
import wbot_commands.roll
import wbot_commands.mtg


class Commands(object):
    commands = {
        wbot_commands.wiki.WikiCommand.NAME:
            wbot_commands.wiki.WikiCommand(),
        wbot_commands.mtg.MTGCommand.NAME:
            wbot_commands.mtg.MTGCommand(),
        wbot_commands.roll.RollCommand.NAME:
            wbot_commands.roll.RollCommand()  # ,
        # wbot_commands.help.HelpCommand.NAME:
        #      wbot_commands.help.HelpCommand()
    }
