import argparse
import logging
import os

import yaml
from colorama import Style, Fore

import cptools.data as data
import cptools.util as cptools_util
from cptools.checker import parse_checker
from cptools.executor import Executor, default_executor_name

parser = argparse.ArgumentParser(description='Compiles and executes a source file on a set of cases')
parser.add_argument('data_file', type=str, help='The test cases, as a .yml file')
parser.add_argument('src_file', type=str, help='The source file to use')
parser.add_argument('-e', '--executor', type=str, help='The executor to use (will use first listed available executor '
                                                       'for the file extension if this option is not specified)',
                    choices=data.get_executors().keys())
parser.add_argument('-a', '--list-all', help='Always display output, even if the case was correct', action='store_true',
                    dest='list_all')
parser.add_argument('-o', '--only-case', help='Only run a single case', type=int,
                    dest='only_case')


def main():
    cptools_util.init_common(parser)
    args = parser.parse_args()
    cptools_util.init_common_options(args, True)

    cfg = data.get_config()

    logging.info(f'Running {args.src_file} using cases from {args.data_file}')
    logging.debug(f'Working directory: {os.getcwd()}')
    logging.debug(f'Timeout: {cfg["timeout"]}')
    logging.debug(f'Display Character Limit: {cfg["char_limit"]}')

    exc_name = args.executor or default_executor_name(args.src_file)
    logging.debug(f'Using executor {exc_name}')
    logging.debug('')

    # Compile
    try:
        exc = Executor(args.src_file, data.get_executor(exc_name))
    except ValueError as e:
        logging.error(e)
        cptools_util.exit()

    if not os.path.exists(args.src_file):
        logging.error('Source file does not exist!')
        cptools_util.exit()

    if exc.is_compiled():
        logging.debug(f'Compile command: {exc.compile_command}')
        logging.info('Compiling...')
    compile_time = exc.setup()
    if exc.is_compiled():
        logging.debug(f'Compile time: {compile_time:.3f}s')

    if not exc.setup_passed:
        logging.error('Compile failed!')
        cptools_util.exit()

    # Load data
    logging.info('Loading test data...')

    if not os.path.exists(args.data_file):
        logging.error('Data file does not exist!')
        cptools_util.exit()

    try:
        with open(args.data_file) as f:
            tests = yaml.unsafe_load(f.read())
            msg = data.validate_data_object(tests)
            if msg:
                logging.error(f'Error while parsing data: {msg}')
                cptools_util.exit()

            cases = tests['cases']
            for i in range(len(cases)):
                if cases[i]['in'][-1] != '\n':
                    cases[i]['in'] += '\n'
                if cases[i]['out'][-1] != '\n':
                    cases[i]['out'] += '\n'
    except KeyError or IndexError:
        logging.error(f'Malformed test data. {Fore.RED}', exc_info=True)
        cptools_util.exit()

    # Checker
    checker = parse_checker(tests['checker'])
    checker.setup()

    # Run program
    if args.only_case:
        if args.only_case >= len(cases):
            logging.error('Case index out of range!')
            cptools_util.exit()
        cases = cases[args.only_case]

    char_limit = data.get_option('char_limit')
    timeout = data.get_option('timeout')

    print()  # For formatting

    for ind, case in enumerate(cases):
        case_in = case['in']
        case_out = case['out']
        try:
            res, elapsed, tle = exc.run(case_in)
        except UnicodeEncodeError:
            logging.error('Invalid character in Input', exc_info=True)
            cptools_util.exit()
        except UnicodeDecodeError:
            logging.error('Invalid character in Output/Error Stream', exc_info=True)
            cptools_util.exit()

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
            def print_stream(label, text, style_before='', style_after=Style.RESET_ALL):
                print(f'== {label} ==\n{style_before}{cptools_util.truncate(text, char_limit)}{style_after}')

            if res.stderr:
                print_stream('Errors', res.stderr, Fore.LIGHTRED_EX)
            print_stream('Input', case_in)
            print_stream('Output', res.stdout)
            if case_out:
                print_stream('Expected Output', case_out)

    # Cleanup
    exc.cleanup()
    cptools_util.exit(0)
