#! /usr/bin/python3
import discord
import wbot_commands.command
import urllib.parse
import requests
import html2text

MAX_MESSAGE_LENGTH = 1500  # TODO move to a better place
_base_url = 'https://en.wikipedia.org/w/api.php'


def do_search(search_text):
    query = _base_url + '?action=query&list=search&format=json' + \
            '&srlimit=10&srsearch={}'.format(
                urllib.parse.quote(search_text, safe='',
                                   encoding='utf-8'))
    print(query)
    resp = requests.get(query)
    if 200 == resp.status_code:  # OK
        results = resp.json()['query']
        if results['searchinfo']['totalhits'] > 0:
            return results['search']
        else:
            return None
    else:
        print('bad response for query {}. HTTP status code: {}'
              .format(query, resp.status_code))
        return None


def get_summary(title):
    query = _base_url + '?action=query&prop=extracts&exintro=1' + \
            '&redirects=1&format=json&titles={}'.format(
                urllib.parse.quote(title, safe='', encoding='utf-8'))
    print(query)
    resp = requests.get(query)
    if 200 == resp.status_code:  # OK
        results = resp.json()['query']['pages']
        for pageid, data in results.items():  # should only be one
            return html2text.html2text(data['extract'])
    else:
        print('bad response for query {}. HTTP status code: {}'
              .format(query, resp.status_code))
        return None


class WikiCommand(wbot_commands.command.Command):
    """Command that retrieves the closest related wiki article summary for a
    given search text.
    """
    NAME = 'wiki'

    def __init__(self):
        wbot_commands.command.Command.__init__(self,
                                               help={
                                                   'name': WikiCommand.NAME,
                                                   'text': 'retrieve the most relevant Wikipedia post for ' + \
                                                           'a given search term.'
                                               })

    def do(self, text):
        """Perform the action described by this command - in this case, search
        Wikipedia and retrieve the most relevant post summary.
        """
        print('WikiCommand search text: {}'.format(text))
        if not text:
            return None
        search_results = do_search(text)
        print('got search results "{}"'.format(search_results))
        if search_results:
            summary = get_summary(search_results[0]['title'])
            if not summary:
                summary = 'Sorry, no results found for "{}" on Wikipedia'.format(text)
            elif len(summary) > MAX_MESSAGE_LENGTH:
                summary = summary[:MAX_MESSAGE_LENGTH] + '...'
            return 'From **Wikipedia**:\n\n{}'.format(summary)
        else:
            return 'Sorry, no results found for "{}" on Wikipedia'.format(text)
