#! /usr/bin/python3
import discord
import argparse
import mtgsdk
import shlex
import wbot_commands.command

class ArgumentParserError(Exception):
    """Custom argparse ArgumentParser exception.
    """

class ThrowingArgumentParser(argparse.ArgumentParser):
    """An ArgumentParser that throws instead of printing and exiting.
    """
    def error(self, message):
        raise ArgumentParserError(message)

class MTGCommand(wbot_commands.command.Command):
    """
    """
    NAME = 'mtg'

    def __init__(self):
        wbot_commands.command.Command.__init__(self,
                                               help={
                                                   'name': MTGCommand.NAME,
                                                   'text': 'Search mtg for cards!'
                                               })
    @staticmethod
    def parse_query_args(query):
        """Parse the given MTG database query
        """
        parser = ThrowingArgumentParser()
        parser.add_argument('-s', '--set', dest='set', action='store',
                            help='The set abbreviation, e.g. jud for judgement', type=str)
        parser.add_argument('-n', '--name', dest='name', action='store',
                            help='The card name or partial name for search.', type=str)


        result = vars(parser.parse_args(query))
        if not result['set'] and not result['name']:
            raise ArgumentParserError(parser.format_help())
        return result

    @staticmethod
    def emojify_cost(mana_cost):
        if not mana_cost:
            return None
        for k, v in {'{W}': '<:whitemana:258399822858551306>',
                     '{R}': '<:redmana:258399822808088596>',
                     '{B}': '<:blackmana:258399822170554378>',
                     '{U}': '<:bluemana:258399822610956288>',
                     '{G}': '<:greenmana:258399822896300032>'}.items():
            mana_cost = mana_cost.replace(k, v)
        print(mana_cost)
        return mana_cost.replace('{', '').replace('}', '')

    def do(self, query):
        """Perform the action described by this command - query an MTG database.
        """
        params = None
        try:
            params = MTGCommand.parse_query_args(shlex.split(query))
            print(params)
        except ArgumentParserError as e:
            print(e)
            return '{}'.format(e)
        except Exception as e:
            print(e.what())
            return 'something went wrong...'

        if not params:
            return 'Invalid query'

        query_builder = mtgsdk.QueryBuilder(mtgsdk.Card)
        if params['set']:
            query_builder = query_builder.where(set=params['set'])
        if params['name']:
            query_builder = query_builder.where(name=params['name'])
        #for k, v in params.items():
        #    if v:
        #        query_builder = query_builder.where(k=v)

        cards = query_builder.where(pagesize=3).all()

        if not cards:
            return 'error retrieving data'

        result = '\n----------------\n'.join(['**{}**: {}\n\n{}\n\nset: {}'.format(c.name,
                  MTGCommand.emojify_cost(c.mana_cost), c.text, c.set) for c in cards])
        return result
