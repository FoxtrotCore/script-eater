### Script Eater

A formatter for FTF scripts to convert them from transcriber notation to pre-formatted aegisub notation.

Requires **Python version 3 or newer** in order to use.

# End-User *(Client)* Stuff

### Stand-alone Script Eater Usage:

`$ python3 script-eater.py <path to raw transcript>`

Each transcript, in the very first line must contain exclusively the episode number such that the formatter can properly label the output. Every line after the first is interpreted as part of the transcript.

_Ex: (023_raw_transcript.txt)_
```
23

ULRICH: Huh three day weekend,
that’s fantastic. Isn’t it?
```

When the script eater is done formatting, it will place in the same directory as the original raw transcript, the file: `XXX_formatted_transcript.txt`

### Discord client commands:

* help: Stop it, get some help!
* format: Format the attached file from transcriber notation to pre-aegisub notation.

# Admin *(Server)* Stuff

### Supported platforms:

 * Linux
 * Windows*

\**The installer scripts are not directly supported on this platform and will likely need to by emulated via CYGWIN OR MINGWIN. This is explicitly because the bot follows the `/opt`, `/var`, `/log` conventions for storing and retrieving configs, logs, etc.*

### Installation:

A set of installation scripts have been provided for your convenience.

1. $ `cd ./script-eater/bin`
2. $ `sudo ./install.sh`

Afterwards, the bot is installed to `/opt/script-eater` and some symlinks are created in `/usr/bin` so you can simply run `script-eater-bot` for the discord server and `script-eater` for a one-time-runtime formatting anywhere on your system.

### Local formatting mechanism:

This is a program that is a part of the bot already but can be run separate from the bot, *(a-la-carte)*. A soft link to the choose script is already provided for you in your `/bin` folder, so you can run the program as-is after installation.

`script-eater [path to transcript]`

### Discord bot server:

No arguments are needed for the server binary to run. however, an environment variable named `SCRIPT_EATER_BOT_TOKEN` must exist on your system before starting the bot and it must have a valid Discord auth token that you can get from the [Discord Developer Portal](https://discordapp.com/developers/applications/).

`script-eater-bot`

*(for persistence, use the following)*

`screen -dmS script-eater-bot script-eater-bot`
