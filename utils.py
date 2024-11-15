import sys
import os

from ev3dev2.sound import Sound

SOUND = Sound()

class _ErrorPrinter:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

_log_file = open("log.txt", 'w')
_printer = _ErrorPrinter(sys.stderr, _log_file)
sys.stderr = _printer

def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)


def reset_console():
    '''Resets the console to the default state'''
    print('\x1Bc', end='')


def set_cursor(visible):
    '''Turn the cursor on or off'''
    if visible:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


def set_font(name):
    '''Sets the console font

    A full list of fonts can be found with `ls /usr/share/consolefonts`
    '''
    os.system('setfont ' + name)

def speak_es(text: str) -> None:
    SOUND.speak(text, "-ves -b1")

def beep() -> None:
    SOUND.beep()
