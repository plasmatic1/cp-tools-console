import argparse
import logging

import cptools.util as cptools_util

parser = argparse.ArgumentParser(description='Stress-tests your solution using a generator and checker')

parser.add_argument('info_file', type=str, help='YML file containing info of the ')
parser.add_argument('-pwd', '--pause-when-done', help='Asks the user to press enter before terminating',
                    action='store_true')
parser.add_argument('-v', '--verbose', help='Verbose mode: shows DEBUG level log messages',
                    action='store_true')

args = parser.parse_args()


def main():
    cptools_util.init_log(args.verbose)
    cptools_util.init_exit(args.pause_on_exit)

    logging.info('Stress tester!')
