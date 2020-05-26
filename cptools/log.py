from colorama import init, Fore
from datetime import datetime


def init_log():
    init(autoreset=True)


def log(line, pref=''):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {pref}{line}')


def success(line):
    log(line, Fore.GREEN)


def error(line):
    log(line, Fore.RED)


def warn(line):
    log(line, Fore.YELLOW)

