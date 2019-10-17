### Script Eater

A formatter for FTF scripts to convert them from transcriber notation to pre-formatted aegisub notation.

Requires **Python version 3 or newer** in order to use.

#### Stand-alone Script Eater Usage:

`$ python3 script-eater.py <path to raw transcript>`

Each transcript, in the very first line must contain exclusively the episode number such that the formatter can properly label the output.

_Ex: (023_raw_transcript.txt)_
```
23

ULRICH: Huh three day weekend,
that’s fantastic. Isn’t it?
```

When the script eater is done formatting, it will place in the same directory as the original raw transcript, the file: `XXX_formatted_transcript.txt`

#### Discord Bot Usage [WIP]

Nothing to see here... *yet* ... Move along...
