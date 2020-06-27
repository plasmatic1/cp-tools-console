import logging
import sys

import coloredlogs

LOG_FORMAT = '[%(asctime)s/%(name)s] %(levelname)s %(message)s'
TIME_FORMAT = '%H:%M:%S'


def init_log(verbose):
    coloredlogs.install(fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
    if verbose:
        coloredlogs.set_level(logging.DEBUG)


pause_on_exit = False


def init_exit(pause_on_exit0):
    global pause_on_exit
    pause_on_exit = pause_on_exit0


def exit(code=-1):
    if pause_on_exit:
        input('\nPress ENTER to continue...')
    sys.exit(code)


def truncate(a_str, width, placeholder=' [...]'):
    if len(a_str) <= width:
        return a_str
    return a_str[:width] + placeholder + '\n'
