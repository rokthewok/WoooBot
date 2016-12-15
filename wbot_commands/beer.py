#! /usr/bin/python3
import discord
import shlex
import requests
import os
import wbot_commands.argumentparser as argumentparser
import wbot_commands.command

class BeerCommand(wbot_commands.command.Command):
    """
    """
    NAME = 'beer'
    BASE_URL = 'http://api.brewerydb.com/v2/'

    def __init__(self):
        wbot_commands.command.Command.__init__(self,
                                               help={
                                                   'name': BeerCommand.NAME,
                                                   'text': 'Search for beers and breweries'
                                               })

    @staticmethod
    def parse_query_args(query):
        """Parse the given beer query
        """
        parser = argumentparser.ThrowingArgumentParser()
        parser.add_argument('-b', '--brewery', dest='brewery', action='store',
                            help='The exact name of a brewery, because we ' +
                                  'can\'t afford the premium version of this api',
                            type=str)
        parser.add_argument('-n', '--name', dest='name', action='store',
                            help='The exact name of a beer.',
                            type=str)


        result = vars(parser.parse_args(query))
        if not result['brewery'] and not result['name']:
            raise argumentparser.ArgumentParserError(parser.format_help())
        return result

    @staticmethod
    def get_brewery(api_key, brewery):
        if not brewery:
            return None
        params = {
                    'key': api_key,
                    'name': brewery
                 }
        response = requests.get(''.join([BeerCommand.BASE_URL, 'breweries']),
                                params=params)
        response.raise_for_status()
        print(response.text)
        return response.json().get('data', None)

    @staticmethod
    def get_beers(api_key, beer):
        if not beer:
            return None
        params = {
                    'key': api_key,
                    'name': beer,
                    'withBreweries': 'Y'
                 }
        response = requests.get(''.join([BeerCommand.BASE_URL, 'beers']),
                                params=params)
        response.raise_for_status()
        print(response.text)
        return response.json().get('data', None)

    @staticmethod
    def select_beer_for_brewery(beers, brewery):
        if not brewery or not beers:
            return beers
        return [b for b in beers
              if difflib.SequenceMatcher(None, b['name'], brewery).ratio() > 0.6]

    @staticmethod
    def make_message(breweries, beer):
        if not breweries:
            return ('**{name}**\nStyle: {style}\nABV: {abv}%\n' +
                    'Brewery: {brewery}\n\n*{description}*\n{label}') \
                               .format(label=beer[0].get('labels', {}).get('medium', '??'),
                                       name=beer[0].get('name', ''),
                                       style=beer[0].get('style', {}).get('name', '??'),
                                       abv=beer[0].get('abv', '??'),
                                       brewery=beer[0]['breweries'][0].get('name', '??'),
                                       description=beer[0].get('description', '??'))
        else:
            return ('**{name}**\nEstablished: {ested}\n\n*{description}*\n{website}') \
                                       .format(name=breweries[0].get('name', '??'),
                                               ested=breweries[0].get('established', '??'),
                                               #locality=breweries[0]['locations'][0]['locality'],
                                               #region=breweries[0]['locations'][0]['region'],
                                               description=breweries[0].get('description', '??'),
                                               website=breweries[0].get('website', '??'))

    def do(self, query):
        """Perform the action described by this command - query an MTG database.
        """
        api_key = os.environ.get('BREWERYDB_API_KEY')
        if not api_key:
            print('Unable to retrieve API key from environment')
            return 'Something went wrong...'

        params = None
        try:
            params = BeerCommand.parse_query_args(shlex.split(query))
            print(params)
        except argumentparser.ArgumentParserError as e:
            print(e)
            return '`{}`'.format(e)
        except Exception as e:
            print(e)
            return 'something went wrong...'

        if not params:
            return 'Invalid query'

        beers = BeerCommand.get_beers(api_key, params['name'])
        beer = BeerCommand.select_beer_for_brewery(beers, params['brewery'])
        breweries = None
        if not params['name']:
            breweries = BeerCommand.get_brewery(api_key, params['brewery'])

        if not beer and not breweries:
            return 'No results found'

        result = BeerCommand.make_message(breweries, beer)

        print(result)
        return result
