import os, asyncio, discord, time
from script_eater import eat
from utilities import log, load_json, Mode

#
# Stuff to use in runtime
#
bot_status = {
    'online': discord.Status.online,
    'offline': discord.Status.offline,
    'idle': discord.Status.idle,
    'dnd': discord.Status.dnd,
}

commands = load_json(os.path.abspath(os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)) + "/config/commands.json")
paths = load_json(os.path.abspath(os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)) + "/config/paths.json")
prefix = 's!'
response_timeout = 5
confirm_emoji = "\u2705"
deny_emoji = "\u26d4"

DEFAULT_BOT_STATUS = 'Pushing paper...'
DEFAULT_WEBSITE = 'https://foxtrotfanatics.com'
DEFAULT_LOGO = 'https://i.imgur.com/3YFyGp6.png'

#
# Discordy things
#
def create_embed(title, description, author=None, color=0x7625d9):
    if(author == None): author = client.user.name
    embed = discord.Embed(title=title, description=description, url=DEFAULT_WEBSITE, color=color)
    embed.set_author(name=author, url=DEFAULT_WEBSITE, icon_url=DEFAULT_LOGO)
    embed.set_thumbnail(url=DEFAULT_LOGO)

    return embed

async def usage(message):
    await confirm_message(message)
    usage_msg = create_embed('FTF Script Eater', 'General usage and commands.')

    for command, data in commands.items():
        if(data[0] != ""): usage_msg.add_field(name=prefix + command + " [" + data[0] + "]", value=data[1], inline=False)
        else: usage_msg.add_field(name=prefix + command, value=data[1], inline=False)

    await message.channel.send(embed=usage_msg)

async def set_default_status(): await set_status(prefix + 'help | ' + DEFAULT_BOT_STATUS, status='idle')

async def set_status(status_message, status='online'):
    activity = discord.Game(status_message)
    await client.change_presence(status=bot_status[status], activity=activity)

async def confirm_message(message): await message.add_reaction(confirm_emoji)
async def deny_message(message): await message.add_reaction(deny_emoji)

#
# Script Eater things
#
async def eat_script(message):
    if(len(message.attachments) > 0):
        all_valid = True
        for att in message.attachments:
            local_path = paths['user_uploads'] + att.filename
            format_path = None
            log(Mode.DEBUG, "Recieved an attatchment: " + att.filename + ":" + str(att.size) + "(" + str(att.id) + ")\n\tSaving to file: " + local_path)
            await att.save(local_path)
            try: format_path = eat(local_path)
            except Exception as e:
                log(Mode.ERROR, str(e))
                await message.channel.send("**<@" + str(message.author.id) + ">**: *" + str(e) + "*")
                all_valid = False
            await message.channel.send(content="**<@" + str(message.author.id) + ">** *Here's that hot-n-steamy transcript you asked for!*", file=discord.File(format_path))

        if(all_valid): await confirm_message(message)
        else: await deny_message(message)
    else: await deny_message(message)

#
# Initialization
#
client = discord.Client()
bot_token = os.getenv('SCRIPT_EATER_BOT_TOKEN')

#
# Discord event stuff
#
@client.event
async def on_connect():
    user = client.user
    log(Mode.INFO, "Logged in as " + str(user))

@client.event
async def on_disconnect():
    #
    # Band-aid fix to destructor issue of scope calls miraculously not working anymore as soon as the
    #   destructor is in scope, ergo files can no longer be opend and saved to
    #
    log(Mode.INFO, "Logging out of discord...\n\tClearing the cached files...")
    cached_files = [ f for f in os.listdir(paths['user_uploads']) ]
    for file in cached_files: os.remove(os.path.join(paths['user_uploads'], file))

@client.event
async def on_ready(): await set_default_status()

@client.event
async def on_typing(channel, user, when): pass

@client.event
async def on_message(message):
    pieces = message.content.split(" ")
    author = message.author
    command = pieces[0][2:]
    args = pieces[1:]

    if(message.content[:2] == prefix):
        log(Mode.INFO, "Message from (" + str(author) + "): \"" + message.content + "\"")

        if(command == 'help'):
            await set_status('Getting help...')
            await usage(message)
        elif(command == 'format'):
            await set_status('Munching on transcript...')
            await eat_script(message)
        else: await deny_message(message)

        await set_default_status()

client.run(bot_token)
