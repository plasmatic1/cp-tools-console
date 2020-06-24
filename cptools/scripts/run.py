import cptools.data as data
import sys
import os
import argparse
import logging
import yaml

from cptools.executor import Executor, default_executor_name

parser = argparse.ArgumentParser(description='Compiles and executes a source file on a set of cases')
parser.add_argument('data_file', type=str, help='The test cases to run the executable on')
parser.add_argument('src_file', type=str, help='The source file to use')
parser.add_argument('-e', '--executor', type=str, help='The executor to use (will use first listed available executor '
                                                       'for the file extension if this option is not specified)',
                    choices=data.get_executors_list())

parser.add_argument('-la', '--list-all', '')

args = parser.parse_args()


def main():
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
        sys.exit(-1)

    logging.info('Compiling...')
    exc.setup()

    if not exc.setup_passed:
        logging.error('Compile failed!')
        sys.exit(-1)

    # Load data
    logging.info('Loading test data...')

    if not os.path.exists(args.data_file):
        logging.error('Data file does not exist!')
        sys.exit(-1)

    with open(args.data_file) as f:
        cases = yaml.unsafe_load(f.read())

    # Run program


    # Cleanup
    logging.info('Cleaning up files...')
    exc.cleanup()

