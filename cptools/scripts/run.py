import argparse
import logging
import os

import yaml
from colorama import Style, Fore

import cptools.data as data
import cptools.common as common
from cptools.checker import parse_checker
from cptools.executor import Executor, default_executor_name, compile_source_file

parser = argparse.ArgumentParser(description='Compiles and executes a source file on a set of cases')
parser.add_argument('data_file', type=str, help='The test cases, as a .yml file')
parser.add_argument('src_file', type=str, help='The source file to use')
parser.add_argument('-e', '--executor', type=str, help='The executor to use (will use first listed available executor '
                                                       'for the file extension if this option is not specified)',
                    choices=data.get_executors().keys())
parser.add_argument('-a', '--list-all', help='Always display output, even if the case was correct', action='store_true')
parser.add_argument('-o', '--only-case', help='Only run a single case', type=int)


def main():
    common.init_common(parser)
    args = parser.parse_args()
    common.init_common_options(args, True)

    cfg = data.get_config()

    logging.info(f'Running {args.src_file} using cases from {args.data_file}')
    logging.debug(f'Working directory: {os.getcwd()}')
    logging.debug(f'Timeout: {cfg["timeout"]}')
    logging.debug(f'Display Character Limit: {cfg["char_limit"]}')

    exc = compile_source_file(args.src_file, args.executor)

    # Load data
    logging.info('Loading test data...')

    if not os.path.exists(args.data_file):
        logging.error('Data file does not exist!')
        common.exit()

    try:
        with open(args.data_file) as f:
            tests = yaml.unsafe_load(f.read())
            msg = data.validate_data_object(tests)
            if msg:
                logging.error(f'Error while parsing data: {msg}')
                common.exit()

            cases = tests['cases']
            for i in range(len(cases)):
                if cases[i]['in'][-1] != '\n':
                    cases[i]['in'] += '\n'
                if cases[i]['out'][-1] != '\n':
                    cases[i]['out'] += '\n'
    except KeyError or IndexError:
        logging.error(f'Malformed test data. {Fore.RED}', exc_info=True)
        common.exit()

    # Checker
    checker = parse_checker(tests['checker'])
    checker.setup()

    # Run program
    if args.only_case is not None:
        if args.only_case >= len(cases):
            logging.error('Case index out of range!')
            common.exit()
        cases = [cases[args.only_case]]
        logging.warning(f'Only running case #{args.only_case}')

    char_limit = data.get_option('char_limit')
    timeout = data.get_option('timeout')

    print()  # For formatting

    verdicts = []
    for ind, case in enumerate(cases):
        case_in = case['in']
        case_out = case['out']
        try:
            res, elapsed, tle = exc.run(case_in)
        except UnicodeEncodeError:
            logging.error('Invalid character in Input', exc_info=True)
            common.exit()
        except UnicodeDecodeError:
            logging.error('Invalid character in Output/Error Stream', exc_info=True)
            common.exit()

        def print_verdict(verdict, verdict_clr, is_timeout=False, extra=''):
            elapsed_str = f'[>{timeout:.3f}s]' if is_timeout else f'[{elapsed:.3f}s]'
            print(f'{Style.BRIGHT}Case #{ind}: {verdict_clr}{verdict}{Style.RESET_ALL + Style.BRIGHT} {extra}{elapsed_str}{Style.RESET_ALL}')

        if tle:
            print_verdict('TLE', Style.DIM + Fore.WHITE, True)
            ac = False
            verdicts.append(Style.DIM + Fore.WHITE + 't')
        elif res.stderr or res.returncode:
            print_verdict('RTE', Fore.YELLOW, False, f'(Exit Code: {res.returncode}) ')
            ac = False
            verdicts.append(Fore.YELLOW + '!')
        else:
            if not case_out and not tests['checker'].startswith('custom'):
                ac, feedback = True, ''
            else:
                ac, feedback = checker.check(case_in, case_out, res.stdout)
            if ac:
                print_verdict('AC', Fore.LIGHTGREEN_EX)
                verdicts.append(Fore.LIGHTGREEN_EX + '*')
            else:
                feedback_str = f'({feedback}) ' if feedback else ''
                print_verdict('WA', Fore.LIGHTRED_EX, False, feedback_str)
                verdicts.append(Fore.LIGHTRED_EX + 'x')

        if not ac or args.list_all:
            def print_stream(label, text, style_before='', style_after=Style.RESET_ALL):
                print(f'== {label} ==\n{style_before}{common.truncate(text, char_limit)}{style_after}')

            if res.stderr:
                print_stream('Errors', res.stderr, Fore.LIGHTRED_EX)
            print_stream('Input', case_in)
            print_stream('Output', res.stdout)
            if case_out:
                print_stream('Expected Output', case_out)

    verdicts = [v + Style.RESET_ALL + Style.BRIGHT for v in verdicts]
    print(f'\n{Style.BRIGHT}Results: [ {" ".join(verdicts)} ]')

    # Cleanup
    exc.cleanup()
    checker.cleanup()
    common.exit(0)
