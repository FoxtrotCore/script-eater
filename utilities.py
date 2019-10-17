from enum import Enum

class Mode(Enum):
    INFO = 0
    DEBUG = 1
    WARN = 2
    ERROR = 3

class Color(Enum):
    HEAD = '\033['

    BLACK = '30m'
    RED = '31m'
    GREEN = '32m'
    YELLOW = '33m'
    BLUE = '34m'
    MAGENTA = '35m'
    CYAN = '36m'
    WHITE = '37m'
    GRAY = '90m'

    B_RED = '91m'
    B_GREEN = '92m'
    B_YELLOW = '93m'
    B_BLUE = '94m'
    B_MAGENTA = '95m'
    B_CYAN = '96m'
    B_WHITE = '97m'

    TAIL = '\033[0m'

    def __add__(self, other):
        if(other is Color): return self.value + other.value
        else: return self.value + str(other)
    def __radd__(self, other): return str(self) + str(other)
    def __repr__(self): return str(self.value)
    def __str__(self):  return str(self.value)

class CString:
    def __init__(self, color, message):
        self.color = color
        self.message = message

    def __add__(self, other): return str(self) + str(other)
    def __radd__(self, other): return str(other) + str(self)
    def __repr__(self): return Color.HEAD + self.color + self.message + str(Color.TAIL)
    def __str__(self):  return Color.HEAD + self.color + self.message + str(Color.TAIL)

def log(mode, message):
    if(isinstance(mode, Mode)):
        if(mode == Mode.INFO): color = Color.GREEN
        elif(mode == Mode.DEBUG): color = Color.BLUE
        elif(mode == Mode.WARN): color = Color.B_YELLOW
        else: color = Color.RED
        print("[" + CString(color, mode.name) + "]: " + CString(Color.B_WHITE, message))
    else: raise TypeError("Expected: (" + str(type(Mode)) + "), got: (" + str(type(mode)) + ")")


def main():
    print("ANSI colors available:")
    for color in Color:
        if(not (color.name in {'HEAD', 'TAIL'})): print("\t" + CString(color, color.name))

if __name__ == '__main__': main()
