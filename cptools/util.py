import logging
import sys

import colorama
import coloredlogs
import cptools.data as data

LOG_FORMAT = '[%(asctime)s/%(name)s] %(levelname)s %(message)s'
TIME_FORMAT = '%H:%M:%S'


pause_when_done = False


def init_common_options(args, validate_executors):
    """
    Does common initialization dependent on command line options.  This includes any initialization that uses the logger
    :param args: From ArgumentParser.parse_args()
    :param validate_executors: Whether to validate if executors is valid as well
    """

    # Init logger based on verbosity
    colorama.init()
    coloredlogs.install(fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
    if args.verbose:
        coloredlogs.set_level(logging.DEBUG)

    # Init pause_on_exist
    global pause_when_done
    pause_when_done = args.pause_when_done

    # Validate config and executors
    msg = data.validate_config_object(data.get_config())
    if msg:
        logging.error(f'Error while parsing config: {msg}')
        exit()
    if validate_executors:
        msg = data.validate_executors_object(data.get_executors())
        if msg:
            logging.error(f'Error while parsing executors: {msg}')
            exit()


def init_common(parser):
    """
    Does common initialization
    :param parser: Argument parser (init_common adds common options to the argument parser)
    """
    parser.add_argument('-pwd', '--pause-when-done', help='Asks the user to press enter before terminating',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose mode: shows DEBUG level log messages',
                        action='store_true')


def exit(code=-1):
    if pause_when_done:
        input('\nPress ENTER to continue...')
    sys.exit(code)


def truncate(a_str, width, placeholder=' [...]'):
    if len(a_str) <= width:
        return a_str
    return a_str[:width] + placeholder + '\n'
