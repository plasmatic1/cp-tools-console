from subprocess import CompletedProcess

import yaml
import os
import argparse
import logging

import cptools.common as common
import cptools.data as data
from cptools.checker import parse_checker
from cptools.executor import compile_source_file

from colorama import Style, Fore

parser = argparse.ArgumentParser(description='Stress-tests your solution using a generator and optional reference '
                                             'solution')

parser.add_argument('config_file', type=str, help='YML file containing info for the generator, reference solution, and '
                                                'solution to be tested')
parser.add_argument('-tg', '--test-generate', help='Run the generator (and reference solution if applicable) ONLY (one '
                                                   'time) and print the generated case',
                        action='store_true')
parser.add_argument('-cl', '--case-limit', help='Only run CASE_LIMIT cases (normally, the stress-tester would keep '
                                                'running until manually terminated (i.e. with Ctrl+C))', type=int, default=-1)
parser.add_argument('-s', '--seed', help='By default, the case number supplied when the --test-generate option is used '
                                         'is 0.  By specifying this option with an integer, that seed will be used '
                                         'instead', type=int, default=0)


def main():
    common.init_common(parser)
    args = parser.parse_args()
    common.init_common_options(args, True)

    if not os.path.exists(args.config_file):
        logging.error(f'Info file {args.config_file} does not exist!')
        common.exit()

    with open(args.config_file) as f:
        info = yaml.unsafe_load(f.read())

    msg = data.validate_stress_test_object(info)
    if msg:
        logging.error(f'Invalid info file: {msg}')
        common.exit()

    # Load generator, slow, and fast
    executors_dict = info.get('executors', dict())
    logging.info('Loading generator...')
    gen_exc = compile_source_file(info['gen'], executors_dict.get('gen'))
    if info.get('slow'):
        logging.info('Loading reference (slow) solution...')
        slow_exc = compile_source_file(info['slow'], executors_dict.get('slow'))
    else:
        logging.warning('No reference solution exists! Reference output will be taken from generator STDERR (Input will be from STDOUT)')
        slow_exc = None
    logging.info('Loading to be tested (fast) solution...')
    fast_exc = compile_source_file(info['fast'], executors_dict.get('fast'))

    # Utils
    def check_proc(seed, proc_name, proc_out: CompletedProcess, is_tle):
        """
        Check if the process TLEd or RTEd and exits CPTools accordingly if so
        :param seed: RNG seed (used for logging)
        :param proc_name: Process name (used for logging)
        :param proc_out: The CompletedProcess object after running the process
        :param is_tle: A bool specifying whether the process TLEd
        """
        if is_tle:
            logging.error(f'Error while generating case using seed {seed}')
            logging.error(f'{proc_name} timed out.  Terminating process...')
            common.exit()
        if proc_out.returncode != 0:
            logging.error(f'Error while generating case using seed {seed}')
            logging.error(f'{proc_name} runtime error (exit code: {proc_out.returncode})')
            logging.error(f'STDERR:\n{proc_out.stderr}')
            common.exit()

    def generate_case(seed):
        """
        Generates a test case using a given seed
        :param seed: The seed (int)
        :return: A tuple (input, output)
        """
        gen_out, _, gen_tle = gen_exc.run('', None, str(seed))
        check_proc(seed, 'Generator', gen_out, gen_tle)

        res_in = gen_out.stdout

        if slow_exc:
            slow_out, _, slow_tle = slow_exc.run(res_in, None, str(seed))
            check_proc(seed, 'Reference solution', slow_out, slow_tle)
            res_out = slow_out.stdout
        else:
            res_out = gen_out.stderr

        return res_in, res_out

    # Test generate
    if args.test_generate:
        logging.info(f'Using seed {args.seed}')
        case_in, case_out = generate_case(args.seed)
        print(f'== Case Input ==\n{case_in}\n== Case Output ==\n{case_out}')
        common.exit(0)

    # Load checker
    checker = parse_checker(info['checker'])
    checker.setup()

    # Run stress test
    i = 0
    while i != args.case_limit:  # If args.case_limit==-1, it will keep going forever since i will never equal -1
        case_in, case_out = generate_case(i)

        def print_case_info():
            print(f'{Style.BRIGHT}== Test Case Info =={Style.RESET_ALL}\n'
                  f'Case Input:\n'
                  f'{case_in}\n'
                  f'Case Output:\n'
                  f'{case_out}')

        proc_out, elapsed, tle = fast_exc.run(case_in)

        if tle:
            print(f'\n{Style.BRIGHT}Case {i} {Style.DIM}TLE{Style.RESET_ALL} (generator seed {i}){Style.RESET_ALL}\n\n'
                  f'Process Output:\n'
                  f'{proc_out.stdout}')
            print_case_info()
            common.exit(0)
        elif proc_out.stderr or proc_out.returncode:
            print(f'\n{Style.BRIGHT}Case {i}: {Fore.YELLOW}RTE{Style.RESET_ALL} (generator seed {i}){Style.RESET_ALL}\n\n'
                  f'Exit Code: {proc_out.returncode}\n'
                  f'Process STDERR:\n'
                  f'{proc_out.stderr}\n'
                  f'Process Output:\n'
                  f'{proc_out.stdout}')
            print_case_info()
            common.exit(0)
        else:
            res, feedback = checker.check(case_in, case_out, proc_out.stdout)
            if res: print(f'Passed case {i}')
            else:
                print(f'\n{Style.BRIGHT}Case {i}: {Fore.RED}WA{Style.RESET_ALL} (generator seed {i}){Style.RESET_ALL}\n\n'
                      f'Process Output:\n'
                      f'{proc_out.stdout}')
                print_case_info()
                common.exit(0)

        i += 1

    print(f'Done {args.case_limit} cases!')

    # Clean up
    gen_exc.cleanup()
    if slow_exc: slow_exc.cleanup()
    fast_exc.cleanup()
    common.exit(0)
