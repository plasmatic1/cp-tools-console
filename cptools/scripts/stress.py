import argparse
import logging

import cptools.util as cptools_util
import cptools.data as data

parser = argparse.ArgumentParser(description='Stress-tests your solution using a generator and checker')

parser.add_argument('info_file', type=str, help='YML file containing info for the generator')
parser.add_argument('-tg', '--test-generate', help='Run the generator ONLY (one time) and print the case',
                        action='store_true')
parser.add_argument('-cl', '--case-limit', help='Only run CASE_LIMIT cases (normally, the stress-tester would keep '
                                                'running until manually terminated (i.e. with Ctrl+C))', type=int)

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
        pass
