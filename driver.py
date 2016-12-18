import discord
import asyncio
import requests
# import apscheduler
import time
import wbot_commands
import os

client = discord.Client()


@client.event
async def on_ready():
    """Listen for on ready event from discord client"""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def parse_cmd_from_text(text):
    words = text.split(' ')

    if len(words) > 1:
        cmd = words[1]
        tail = words[2:]
        text = ''
        if len(tail) != 0:
            text = ' '.join(tail)

        return cmd, text
    else:
        return None, None


@client.event
async def on_message(message):
    text = message.content

    if text.startswith('!wbot'):
        cmd_name, text = parse_cmd_from_text(text)
        print('cmd: "{}"'.format(cmd_name))
        print('text: "{}"'.format(text))
        command = wbot_commands.Commands.commands.get(cmd_name)
        try:
            outgoing_message = command.do(text)
            await client.send_message(message.channel, outgoing_message)
        except AttributeError as e:
            print('{}'.format(e))
            await client.send_message(message.channel, 'sorry, bad command')
        except Exception as e:
            print('exception: {}'.format(e))
            await client.send_message(message.channel, 'sorry, something went wrong')


if __name__ == '__main__':
    token = os.environ.get('TEST_DISCORD_TOKEN')

    if token is not None:
        client.run(token)
    else:
        print('ERROR: unable to retrieve discord token.')
