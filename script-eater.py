import discord
import signal
import sys
import os

json_config_path = "~/.ftf-"
debug = True
client = discord.Client()
prefix = "se!"
bot_token = os.getenv('FTF_SCRIPT_EATER_TOKEN')

def check_dir(filepath):
    if(os.path.isdir(filepath)):
        say(0, "Path: " + filepath + " was found!")
    else:
        say(1, "Path: " + filepath + " was not found!\n\tCreating now...")
        os.mkdir(filepath, 700)

def check_file(filepath):
    if(os.path.exists(filepath)):
        say(0, "File: " + filepath + " was found!")
    else:
        say(2, "Something went wrong when trying to find the input file: " + filepath + "!\n\tTerminating early!")
        exit(2)

def loadConfig(filepath):
    check_dir(filepath)

def signal_handler():
    print("\n")
    say(1, "Goodbye!")
    client.logout()
    exit(0)

def say(arg_mode, message):
    mode = {
            0: "INFO",
            1: "WARN",
            2: "ERROR",
            3: "DEBUG"
        }

    print("[" + mode[arg_mode] + "]: " + message)

#
# Discord Bot Events
#
@client.event
async def on_ready():
    say(0, 'Logged into server with\n\tName: ' + client.user.name + '\n\tID: <@' + client.user.id + ">")

@client.event
async def on_message(message):
    global prefix
    bot_response = ""

    if message.author == client.user:
        return

    if(debug == True):
        say(3, "A message has been recieved: " + message.content)

    if message.content.startswith(prefix + 'hello'):
        bot_response = 'Hello {0.author.mention}'.format(message)
    elif message.content.startswith(prefix + 'ring'):
        bot_response = 'Banana phone!'.format(message)
    elif message.content.startswith(prefix + 'prefix'):
        new_prefix = message.content.split(' ')[1]
        client.add_reaction(message.id, 'white_check_mark')
        bot_response = "Changed prefix from: " + prefix + " to: " + new_prefix + "".format(message)
        say(0, "Changing prefix\n\tFrom: " + prefix + "\n\tTo: " + new_prefix)
        prefix = new_prefix
    elif message.content.startswith(prefix + 'invite'):
        bot_response = 'https://discordapp.com/api/oauth2/authorize?client_id=550099565043515397&scope=bot'.format(message)
    elif message.content.startswith(prefix + 'commitdie'):
        for i in client.servers:
            await client.send_message(message.channel, i.name)

    if bot_response != "":
        await client.send_message(message.channel, bot_response)

#
# System events
#
client.run(bot_token)
signal.signal(signal.SIGINT, signal_handler())
