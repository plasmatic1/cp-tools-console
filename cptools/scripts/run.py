import cptools.data as data
import os
import argparse
import logging
import yaml

from cptools.checker import parse_checker
from cptools.executor import Executor, default_executor_name
from colorama import Style, Fore
import colorama
import cptools.util as cptools_util

parser = argparse.ArgumentParser(description='Compiles and executes a source file on a set of cases')
parser.add_argument('data_file', type=str, help='The test cases to run the executable on')
parser.add_argument('src_file', type=str, help='The source file to use')
parser.add_argument('-e', '--executor', type=str, help='The executor to use (will use first listed available executor '
                                                       'for the file extension if this option is not specified)',
                    choices=data.get_executors_list())
parser.add_argument('-a', '--list-all', help='Always display output, even if the case was correct', action='store_true',
                    dest='list_all')
parser.add_argument('-o', '--only-case', help='Only run a single case', type=int,
                    dest='only_case')
parser.add_argument('-pwd', '--pause-when-done', help='Asks the user to press enter before terminating',
                    action='store_true')

args = parser.parse_args()


def main():
    colorama.init()
    cptools_util.init_log()
    cptools_util.init_exit(args.pause_when_done)

    cfg = data.get_config()

    logging.info(f'Running {args.src_file} using cases from {args.data_file}')
    logging.debug(f'Working directory: {os.getcwd()}')
    logging.debug(f'Timeout: {cfg["timeout"]}')
    logging.debug(f'Display Character Limit: {cfg["char_limit"]}')

    exc_name = args.executor or default_executor_name(args.src_file)
    logging.debug(f'Using executor {exc_name}')
    logging.debug('')

    # Compile
    exc = Executor(args.src_file, data.get_executor(exc_name))

    if not os.path.exists(args.src_file):
        logging.error('Source file does not exist!')
        cptools_util.exit()

    if exc.is_compiled():
        logging.info('Compiling...')
        exc.setup()

    if not exc.setup_passed:
        logging.error('Compile failed!')
        cptools_util.exit()

    # Load data
    logging.info('Loading test data...')

    if not os.path.exists(args.data_file):
        logging.error('Data file does not exist!')
        cptools_util.exit()

    with open(args.data_file) as f:
        tests = yaml.unsafe_load(f.read())
        cases = tests['cases']
        for i in range(len(cases)):
            if cases[i]['in'][-1] != '\n':
                cases[i]['in'] += '\n'
            if cases[i]['out'][-1] != '\n':
                cases[i]['out'] += '\n'

    # Checker
    checker = parse_checker(tests['checker'])
    checker.setup()

    # Run program
    if args.only_case:
        if args.only_case >= len(cases):
            logging.error('Case index out of range!')
            cptools_util.exit()
        cases = cases[args.only_case]

    for ind, case in enumerate(cases):
        case_in = case['in']
        case_out = case['out']
        timeout = data.get_option('timeout')
        res, elapsed, tle = exc.run(case_in)

        def print_verdict(verdict, verdict_clr, is_timeout=False, extra=''):
            elapsed_str = f'[>{timeout:.3f}s]' if is_timeout else f'[{elapsed:.3f}s]'
            print(f'{Style.BRIGHT}Case #{ind}: {verdict_clr}{verdict}{Style.RESET_ALL + Style.BRIGHT} {extra}{elapsed_str}{Style.RESET_ALL}')

        if tle:
            print_verdict('TLE', Style.DIM + Fore.WHITE, True)
            ac = False
        elif res.stderr or res.returncode:
            print_verdict('RTE', Fore.YELLOW, False, f'(Exit Code: {res.returncode}) ')
            ac = False
        else:
            if not case_out and not tests['checker'].startswith('custom'):
                ac, feedback = True, ''
            else:
                ac, feedback = checker.check(case_in, case_out, res.stdout)
            if ac:
                print_verdict('AC', Fore.LIGHTGREEN_EX)
            else:
                feedback_str = f'({feedback}) ' if feedback else ''
                print_verdict('WA', Fore.LIGHTRED_EX, False, feedback_str)

        if not ac or args.list_all:
            if res.stderr:
                print(f'== Errors ==\n{Fore.LIGHTRED_EX + res.stderr + Style.RESET_ALL}')
            print(f'== Input ==\n{case_in}')
            print(f'== Output ==\n{res.stdout}')
            if case_out:
                print(f'== Expected Output ==\n{case_out}')

    # Cleanup
    exc.cleanup()
    cptools_util.exit(0)
