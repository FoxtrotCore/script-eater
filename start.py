#!/usr/bin/env python3
import os, sys
from script_eater import ScriptEater
from ftf_utilities import Mode, log, load_json, dump_json

def load_token(path):
    if(not os.path.exists(path)):
        dump_json(path, {'token': ''})
        log(Mode.ERROR, "Missing token in config: " + path \
                        + '\n\tPlease add a Discord Bot Token to this file before relaunching the bot.' \
                        + '\n\t(You can generate a token from here: https://discordapp.com/developers/applications)')
        sys.exit(-1)

    token = load_json(path)['token']

    if(token == None or token == ''):
        log(Mode.ERROR, "Missing token in config: " + path \
                        + '\n\tPlease add a Discord Bot Token to this file before relaunching the bot.' \
                        + '\n\t(You can generate a token from here: https://discordapp.com/developers/applications)')
        sys.exit(-1)
    return token

config = load_json('res/meta.json')
commands = load_json('res/commands.json')
conf_dir = os.path.expanduser(config['conf_dir'])
token_path =  conf_dir + os.sep + 'token.json'
cache_dir = conf_dir + os.sep + 'cache'

if(not os.path.exists(cache_dir)):
    # Generate the cache directory
    log(Mode.WARN, 'Cache dir notc found: ' + str(cache_dir) + '\n\tAutomatically generating...')
    os.makedirs(conf_dir)
    os.makedirs(cache_dir)

# Load the token cfg and subsequent token.
token = load_token(token_path)

conf = [conf_dir, cache_dir]
bot = ScriptEater(token, commands, conf)
bot.run()
