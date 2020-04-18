import asyncio, os
from time import ctime
from discord import *
from ftf_utilities import Mode, log

CONFIRM_EMOJI = "\u2705"
DENY_EMOJI = "\u26d4"

class ScriptEater(Client):
    def __init__(self, token,
                       commands,
                       conf,
                       verbose = False,
                       prefix = "s!",
                       message = "Hungry for scripts...",
                       website = "https://foxtrotfanatics.com",
                       color = 0xfce91b):
        super().__init__()

        self.token = token
        self.commands = commands
        self.cache_dir = conf[1]
        self.verbose = verbose
        self.prefix = prefix
        self.message = message
        self.website = website
        self.color = color

        ScriptEater.LOG_DIR = conf[0]

    # Static functions
    def log_file(mode, msg):
        log(mode, msg)

        if(mode == Mode.INFO): log_path = ScriptEater.LOG_DIR + os.sep + 'info.log'
        elif(mode == Mode.WARN): log_path = ScriptEater.LOG_DIR + os.sep + 'warn.log'
        elif(mode == Mode.DEBUG): log_path = ScriptEater.LOG_DIR + os.sep + 'debug.log'
        elif(mode == Mode.ERROR): log_path = ScriptEater.LOG_DIR + os.sep + 'error.log'
        else: log_path = ScriptEater.LOG_DIR + os.sep + 'misc.log'

        file = open(log_path, 'a')
        file.write("[" + ctime() + "]: " + msg + "\n")
        file.close()

    def is_empty(string): return (string == '' or string == None)

    async def confirm_message(message): await message.add_reaction(CONFIRM_EMOJI)
    async def deny_message(message): await message.add_reaction(DENY_EMOJI)

    # Instance Functions
    def run(self):
        ScriptEater.log_file(Mode.INFO, "Logging into Discord...")
        asyncio.get_event_loop().run_until_complete(super().run(self.token))

    def eat(self, path):
        abs_path = os.path.abspath(path)
        parent_dir = os.path.dirname(abs_path)
        if(not os.path.exists(abs_path)): raise FileNotFoundError("File: " + abs_path + " does not exist!")

        ScriptEater.log_file(Mode.INFO, "Opening file for parsing: " + abs_path)

        # Transcript line storage
        raw_lines = []
        processed_lines = []

        file = open(abs_path)
        episode_number = file.readline().strip()
        print()
        if(self.verbose): ScriptEater.log_file(Mode.DEBUG, "ep: " + str(episode_number))
        if(not episode_number.isdigit()): raise IOError("Transcript: " + path.split('/')[-1] + " (line 1) has invalid episode header:\"" + episode_number + "\"\n\tThe first line of the transcript must contain exclusively the alphanumeric episode number")

        episode_number = str(episode_number).rjust(3, '0') # Padding ep number

        # User info
        ScriptEater.log_file(Mode.INFO, "Processing episode " + episode_number)
        for line in file: raw_lines.append(line.strip())
        file.close()

        num = 2
        case = 0
        line_1 = None
        line_2 = None

        # Process Line combination
        while(len(raw_lines) > 0):
            # Grab more lines from the file as needed
            if(case != 2):
                line_1 = raw_lines.pop(0)
                num = num + 1
            if(len(raw_lines) > 0):
                line_2 = raw_lines.pop(0)
                num = num + 1
            else: line_2 = ''

            # Process the lineup case and append or shift accordingly
            if(ScriptEater.is_empty(line_1) and ScriptEater.is_empty(line_2)):
                case = 0
            elif(not ScriptEater.is_empty(line_1) and ScriptEater.is_empty(line_2)):
                processed_lines.append(line_1)
                case = 1
            elif(ScriptEater.is_empty(line_1) and not ScriptEater.is_empty(line_2)):
                line_1 = line_2
                case = 2
            elif(not ScriptEater.is_empty(line_1) and not ScriptEater.is_empty(line_2)):
                line = line_1 + '\\N' + line_2
                processed_lines.append(line)
                case = 3

        last_badge = ''
        # Find badgeless lines and give them the last known one
        for i, line in enumerate(processed_lines):
            has_badge = (len(line.split(':')) == 2)
            if(has_badge): last_badge = line.split(':')[0]
            else: processed_lines[i] = last_badge + ": " + line

        # Figure out output path
        out_path = parent_dir + '/' + str(episode_number) + '_formatted_transcript.txt'
        ScriptEater.log_file(Mode.INFO, "Writing out to file: " + out_path)

        # Create Formatted output
        out_file = open(out_path, 'w+')
        for line in processed_lines: out_file.write(line + "\n")
        out_file.close()
        return out_path

    async def format(self, message):
        if(len(message.attachments) > 0):
            all_valid = True
            for att in message.attachments:
                local_path = self.cache_dir + os.sep + att.filename
                format_path = None
                ScriptEater.log_file(Mode.DEBUG, "Received an attatchment: " + att.filename + ":" + str(att.size) + "(" + str(att.id) + ")\n\tSaving to file: " + local_path)
                await att.save(local_path)
                try: format_path = self.eat(local_path)
                except Exception as e:
                    ScriptEater.log_file(Mode.ERROR, str(e))
                    await message.channel.send("**<@" + str(message.author.id) + ">**: *" + str(e) + "*")
                    all_valid = False
                await message.channel.send(content="**<@" + str(message.author.id) + ">** *Here's that hot-n-steamy transcript you asked for!*", file=File(format_path))

            if(all_valid): await ScriptEater.confirm_message(message)
            else: await ScriptEater.deny_message(message)
        else: await ScriptEater.deny_message(message)

    def create_embed(self, title, description, author = None):
        if(author is None): author = self.user.name
        embed = Embed(title = title,
                      description = description,
                      url = self.website,
                      color = self.color)
        embed.set_author(name = author,
                         url = self.website)
        return embed

    async def usage(self, message):
        await ScriptEater.confirm_message(message)
        usage_msg = self.create_embed('Script Eater', 'General usage and commands.')

        for command, data in self.commands.items():
            if(data[0] != ""): usage_msg.add_field(name = self.prefix + command + " [" + data[0] + "]",
                                                   value = data[1],
                                                   inline = False)
            else: usage_msg.add_field(name = self.prefix + command,
                                      value = data[1],
                                      inline = False)

        await message.channel.send(embed = usage_msg)

    async def set_default_status(self):
        await self.set_status(self.prefix + "help | " + self.message, status=Status.idle)

    async def set_status(self, message, status = Status.idle):
        await self.change_presence(status = status, activity = Game(message, type=ActivityType.watching))

    async def on_ready(self):
        ScriptEater.log_file(Mode.INFO, "Logged in as " + str(self.user))
        await self.set_default_status()

    async def on_disconnect(self):
        CivBot.log_file(Mode.WARN, "Shutting down Script Eater!")

    async def on_message(self, message):
        pieces = message.content.split(" ")
        author = message.author
        guild = message.guild
        command = pieces[0][2:]
        args = pieces[1:]

        if(message.content[:2] == self.prefix):
            ScriptEater.log_file(Mode.INFO, "Message from (" + str(author) + ") in [" + str(guild) + "(" + str(guild.id) + ")]: \"" + message.content + "\"")

            if(command == 'help'):
                await self.set_status('Getting help...')
                await self.usage(message)
            elif(command == 'format'):
                await self.set_status('Munching on script...')
                await self.format(message)
            else: await ScriptEater.deny_message(message)
        await self.set_default_status()
