#! /usr/bin/python3
import discord
import mtgsdk
import shlex
import wbot_commands.argumentparser as argumentparser
import wbot_commands.command


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
        parser = argumentparser.ThrowingArgumentParser()
        parser.add_argument('-s', '--set', dest='set', action='store',
                            help='The set abbreviation, e.g. jud for judgement',
                            type=str)
        parser.add_argument('-n', '--name', dest='name', action='store',
                            help='The card name or partial name for search.',
                            type=str)


        result = vars(parser.parse_args(query))
        if not result['set'] and not result['name']:
            raise argumentparser.ArgumentParserError(parser.format_help())
        return result

    @staticmethod
    def emojify(mana_cost):
        if not mana_cost:
            return None
        for k, v in {'{W}': '<:whitemana:258399822858551306>',
                     '{R}': '<:redmana:258399822808088596>',
                     '{B}': '<:blackmana:258399822170554378>',
                     '{U}': '<:bluemana:258399822610956288>',
                     '{G}': '<:greenmana:258399822896300032>',
                     '{B/G}': '<:bgmana:258755977740812288>',
                     '{B/R}': '<:brmana:258755977405267970>',
                     '{G/U}': '<:gumana:258755977317187603>',
                     '{G/W}': '<:gwmana:258755977749200896>',
                     '{R/G}': '<:rgmana:258755977812246528>',
                     '{R/W}': '<:rwmana:258755977300541444>',
                     '{U/B}': '<:ubmana:258755977740943360>',
                     '{U/R}': '<:urmana:258755977241690115>',
                     '{W/B}': '<:wbmana:258755977317318658>',
                     '{W/U}': '<:wumana:258755979598888960>',
                     '{T}': '<:tap:258399822300708874>'}.items():

            mana_cost = mana_cost.replace(k, v)
        print(mana_cost)
        return mana_cost

    def do(self, query):
        """Perform the action described by this command - query an MTG database.
        """
        params = None
        try:
            params = MTGCommand.parse_query_args(shlex.split(query))
            print(params)
        except argumentparser.ArgumentParserError as e:
            print(e)
            return '`{}`'.format(e)
        except Exception as e:
            print(e)
            return 'something went wrong...'

        if not params:
            return 'Invalid query'

        cards = mtgsdk.Card.where(**{k: v for k, v in params.items() if v}) \
                           .where(page=1) \
                           .where(pageSize=3).all()

        if not cards:
            return 'error retrieving data'

        result = '\n----------------\n'.join(
                ['**{name}**: {cost}\n\n*{type}*\n{text}\n\nset: {set}'.format(
                  name=c.name,
                  cost=MTGCommand.emojify(c.mana_cost), type=c.type,
                  text=MTGCommand.emojify(c.text if c.text else ''),
                  set=c.set) for c in cards])
        return result
