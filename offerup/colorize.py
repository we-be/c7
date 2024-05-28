import sys

# Define color codes
COLORS = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
    'reset': '\033[0m'
}


def colorize(color, *args):
    if color not in COLORS:
        raise ValueError(f"Invalid color: {color}")

    color_code = COLORS[color]
    reset_code = COLORS['reset']
    colored_text = ' '.join(str(arg) for arg in args)

    return f"{color_code}{colored_text}{reset_code}"


def cprint(color, *args):
    colored_text = colorize(color, *args)
    print(colored_text + COLORS['reset'])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python colorize.py <color> <text>")
        sys.exit(1)

    _color = sys.argv[1].lower()
    text = sys.argv[2:]

    cprint(_color, *text)
