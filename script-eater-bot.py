import discord
import asyncio
import json
import os
import signal
import sys

#
# Globals
#
config = {}
config_path = '~/.script-eater/config.json'

#
# Local utility stuff
#

def say(arg_mode, message):
    mode = {
            0: 'INFO',
            1: 'WARN',
            2: 'DEBUG',
            3: 'ERROR'
        }

    print('[' + mode[arg_mode] + ']: ' + message)

def fix_path(filename):
    if(filename[0] == '~'):
        return os.path.expanduser(filename)
    elif(filename[0] == '.'):
        return os.path.realpath(filename)
    else:
        return filename

def load_config(filename):
    config_file = open(filename, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
    config = json.loads(config_file.read())
    config_file.close()

    config['response-timeout'] = float(config['response-timeout'])

    return config

def save_config(filename):
    global config

    dumpable_data = json.dumps(config, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=4, separators=None, default=None, sort_keys=True)

    if(config['debug']):
        say(2, dumpable_data)

    config_file = open(filename, mode='w', buffering=-1, encoding=None, errors=None, newline='\n', closefd=True)
    config_file.write(dumpable_data)
    config_file.close()

def update_default_bot_status():
    global config
    global active_bot_status
    active_bot_status = config['prefix'] + "help" + " | " + config['bot-status']

def handle_forced_exit():
    global client
    global config_path

    print('\n')
    say(0, 'A signal was received to shutdown the bot!')
    save_config(config_path)
    client.logout()
    sys.exit(0)

def message_prefix(message):
    return message[0:len(config['prefix'])]

def message_suffix(message):
    return message[len(config['prefix']):].split(' ')[0]

def message_argument(message):
    return message[len(config['prefix']):].split(' ')[1]

def is_command(message):
    return (message_prefix(message) == config['prefix'])

def is_admin(user_id):
    global admins

    for i in admins:
        if(user_id == i):
            return True
    return False

def get_command_map(message):
    index = 0

    for i in commands.keys():
        if(message_suffix(message) == i):
            return index
        else:
            index = index + 1
    return (-1)

def load_servers():
    global client

    say(0, 'Script Eater has joined a total of ' + str(len(client.servers)) + ' servers!')
    for i in client.servers:
        print('\t\"' + i.name + '\" in ' + str(i.region) + ' with ' + str(len(i.members)) + ' people')

def load_admins():
    global client
    global config
    global admins

    for i in config['admins']:
        admins.append(client.get_user_info(i))
        # say(1, "Adding " + str(client.get_user_info(i).name))

def load_emojis():
    global client
    global emojis

    say(0, 'Loading up custom emojis...')
    for i in client.get_all_emojis():
        emojis.append(i)
    say(0, str(len(emojis)) + ' custom emojis were loaded!')

async def send_config(message):
    global client
    global config_path

    await client.send_file(message.channel, config_path, content=None)

async def set_status(status_message, new_status):
    global client
    global ftf_website

    status = discord.Game(name=status_message, url=ftf_website, type=0)
    await client.change_presence(game=status, status=new_status, afk=False)

async def resolve_confirmation(message, question):
    global client
    global config

    response = await client.send_message(message.channel, content=(question))
    await client.add_reaction(response, config['confirm-emoji'])
    await client.add_reaction(response, config['deny-emoji'])

    resolution = await client.wait_for_reaction(emoji=[config['confirm-emoji'], config['deny-emoji']], message=response, user=message.author, timeout=config['response-timeout'])
    await client.delete_message(response)

    if(resolution == None):
        return None
    elif(resolution[0].emoji == config['confirm-emoji']):
        return True
    elif(resolution[0].emoji == config['deny-emoji']):
        return False
    else:
        say(3, "Reaction confirmation could not resolve!")
        raise "REACTION CONFIRMATION COULD NOT RESLOVE"

async def usage(message):
    global client
    global config

    help_message = discord.Embed(title='Script Eater Help', url=ftf_website, description='Command info and details.', color=0x58ff00)
    help_message.set_author(name='Script Eater', url=ftf_website, icon_url=ftf_logo_url)
    help_message.set_thumbnail(url=ftf_logo_url)

    for command in commands.keys():
        help_message.add_field(name=str(config['prefix'] + command), value=str(commands[command]), inline=False)

    if(config['debug']):
        say(2, '' + str(message.channel) + '\t' + str(message.server) + '\t' + str(message.mention_everyone))

    await client.delete_message(message)
    await client.send_message(message.channel, content=None, embed=help_message)

async def set_new_prefix(message):
    global config
    global client

    # Check if user has permission to do this
    if(is_admin(message.author.id)):
        try:
            argument = message_argument(message.content)
        except:
            say(3, "No argument was given for the prefix command!\n\tTerminating the thread early!")
            await client.delete_message(message)
            await client.send_message(message.channel, content='**Incorrect usage! Please specify a new prefix!**')
            return

        resolution = await resolve_confirmation(message, "**Set new prefix to \"" + argument + "\"?**")

        if(resolution == None):
            say(3, "No response was given!\n\tTerminating the thread early!")
            await client.send_message(message.channel, content='**No response was given! Canceling request...**')
        elif(resolution == True):
            config['prefix'] = argument
            update_default_bot_status()
            await client.send_message(message.channel, content='**Changed prefix to: \"' + argument + "\"!**")
        elif(resolution == False):
            await client.send_message(message.channel, content='**Keeping prefix as ' + config['prefix'] + '**')
    else:
        await client.send_message(message.channel, content='**Must be an admin to do this!**')

    await client.delete_message(message)

async def format_script(message):
    await asyncio.sleep(10)
    return

async def revert_config(message):
    global client
    global config
    global config_path

    if(is_admin(message.author.id)):
        config = load_config(config_path)
        update_default_bot_status()
        await client.send_message(message.channel, content='**Reverted bot config to settings on-file!**')
    else:
        await client.send_message(message.channel, content='**Must be an admin to do this!**')

    await client.delete_message(message)

async def bad_command(message):
    global client

    say(1, 'Script Eater cannot process this command: ' + message.content + '\n\tIgnoring!')
    await client.delete_message(message)
    await client.send_message(message.channel, content=('**<@' + str(message.author.id) + '> Bad command: \"' + message_prefix(message.content) + message_suffix(message.content) + '\"!** *(Try using ' + message_prefix(message.content) + "help for correct usage)*"))

#
# Initialization
#
config_path = fix_path(config_path)
config = load_config(config_path)
client = discord.Client()
bot_token = os.getenv('SCRIPT_EATER_TOKEN')

#
# Stuff to use in runtime
#
active_bot_status = ''
admins = []
emojis = []
ftf_website = 'https://foxtrotfanatics.info'
ftf_logo_url = 'https://media.foxtrotfanatics.info/i/ftf_logo.png'
commands = config['commands']
prefix = config['prefix']
update_default_bot_status()

#
# Discord event stuff
#

@client.event
async def on_ready():
    global config

    say(0, 'Client logged in as the user ' + str(client.user) + '\n\tID: ' + str(client.user.id) + '\n\tBOT: ' + str(client.user.bot) + '\n\tDisplay Name: ' + str(client.user.display_name))
    load_servers()
    load_admins()
    load_emojis()
    await set_status(active_bot_status, discord.Status.idle)

@client.event
async def on_message(message):
    global config

    # Check if message has correct prefix
    if(is_command(message.content)):
        # Console confirmation that a relevant command was received
        say(0, 'Timestamp(' + str(message.timestamp) + ') UserID(' + str(message.author) + ') Message(' + message.content + ')')

        # Get the action map of the command suffix
        map = get_command_map(message.content)

        if(map == 0): # addAdmin
            await set_status('Adding a new admin...', discord.Status.dnd)
        elif(map == 1): # admins
            await set_status('Getting admins...', discord.Status.dnd)
        elif(map == 2): # format
            await set_status('Formatting script...', discord.Status.dnd)
            await format_script(message)
        elif(map == 3): # help
            await set_status('Prepairing help...', discord.Status.dnd)
            await usage(message)
        elif(map == 4): # prefix
            await set_status('Waiting for response...', discord.Status.dnd)
            await set_new_prefix(message)
        elif(map == 5): # removeAdmin
            await set_status('Removing old admin...', discord.Status.dnd)
        elif(map == 6): # revertConfig
            await set_status('Overwiting config...', discord.Status.dnd)
            await revert_config(message)
        else:
            await bad_command(message)

        await set_status(active_bot_status, discord.Status.idle)

client.run(bot_token)
signal.signal(signal.SIGINT, handle_forced_exit())
