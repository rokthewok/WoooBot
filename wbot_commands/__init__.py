#! /usr/bin/python3
import wbot_commands.wiki

class Commands(object):
  commands = {
                wbot_commands.wiki.WikiCommand.NAME:
                      wbot_commands.wiki.WikiCommand()
             }
