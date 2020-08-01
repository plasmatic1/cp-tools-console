import yaml
import os
import argparse
import logging

import cptools.util as cptools_util
import cptools.data as data
from cptools.checker import parse_checker
from cptools.executor import compile_source_file

parser = argparse.ArgumentParser(description='Stress-tests your solution using a generator and checker')

parser.add_argument('info_file', type=str, help='YML file containing info for the generator')
parser.add_argument('-tg', '--test-generate', help='Run the generator ONLY (one time) and print the case',
                        action='store_true')
parser.add_argument('-cl', '--case-limit', help='Only run CASE_LIMIT cases (normally, the stress-tester would keep '
                                                'running until manually terminated (i.e. with Ctrl+C))', type=int)
parser.add_argument('-sr', '--seed-rng', help='The case number will be passed as ARGV[1] to both the generator and '
                                              'solution when they\'re run, allowing them to use a set seed for their '
                                              'RNG', action='store_true')

parser.add_argument('-mf', '--make-file', help='Generates an info_file for stress-testing (which can be configured to'
                                               'your needs).  No stress-testing will actually be done.  The path of the'
                                               ' file is specified by MAKE_FILE',
                        type=str)


def main():
    cptools_util.init_common(parser)
    args = parser.parse_args()
    cptools_util.init_common_options(args, True)

    if args.make_file:
        logging.info(f'Making info file {args.make_file}...')
        with open(args.make_file, 'w') as f:
            f.write(data.get_default_stress_test_file())
    else:
        if not os.path.exists(args.info_file):
            logging.error(f'Info file {args.info_file} does not exist!')
            cptools_util.exit()

        with open(args.info_file) as f:
            info = yaml.unsafe_load(f.read())

        msg = data.validate_stress_test_object(info)
        if msg:
            logging.error(f'Invalid info file: {msg}')
            cptools_util.exit()

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

        # Load checker
        checker = parse_checker(info['checker'])
        checker.setup()

        # Run stress test
        ctr = 0
        case_limit = args.case_limit or -1
        while ctr != case_limit:
            ctr += 1

        print(f'Done {case_limit} cases!')
