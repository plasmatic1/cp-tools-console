import logging
import sys
import cptools.util as util

import cptools.data as data
from cptools.executor import Executor, default_executor_name


class Checker:
    def __init__(self, *_):
        pass

    def setup(self):
        pass

    def cleanup(self):
        pass

    def check(self, input, expected, output):
        res = self._check(input, expected, output)
        if type(res) == str:
            return False, res
        elif type(res) == bool:
            return res, ''

    def _check(self, input, expected, output):
        return True


class IdenticalChecker(Checker):
    def _check(self, _, expected, output):
        return expected == output


class TokensChecker(Checker):
    def _check(self, _, expected, output):
        return expected.split() == output.split()


class FloatChecker(Checker):
    def __init__(self, eps):
        self.eps = float(eps)

    def _check(self, _, expected, output):
        try:
            return all(map(lambda tup: abs(float(tup[0]) - float(tup[1])) < self.eps, zip(expected.split(), output.split())))
        except ValueError as e:
            return str(e)


class CustomChecker(Checker):
    def __init__(self, src_path, exc_name=None):
        self.src_path = src_path
        self.exc = Executor(self.src_path, data.get_executor(exc_name or default_executor_name(src_path)))

    def setup(self):
        if self.exc.is_compiled():
            logging.info('Compiling checker...')
            self.exc.setup()
        if not self.exc.setup_passed:
            logging.error('Checker compile failed!')
            util.exit()

    def _check(self, input, expected, output):
        res, _, tle = self.exc.run('', self.exc.executor_info['command'] + [input, expected, output])

        if tle:
            logging.error(f'Checker timed out')
            util.exit()
        elif res.returncode or res.stderr:
            logging.error(f'Checker encountered runtime error (exit code: {res.returncode})')
            logging.error(f'STDERR info: {res.stderr}')
            util.exit()

        if res.stdout != 'OK':
            return res.stdout
        else:
            return True

    def cleanup(self):
        self.exc.cleanup()


CHECKERS = {
    'tokens': TokensChecker,
    'identical': IdenticalChecker,
    'float': FloatChecker,
    'custom': CustomChecker
}


def parse_checker(checker_str):
    c_type, *c_arg = checker_str.split(':')
    c_arg = ':'.join(c_arg)

    if c_type not in CHECKERS:
        logging.error(f'Invalid checker type {c_type}')
        logging.error(f'Must be one of the following: {CHECKERS.keys()}')
        sys.exit(-1)

    return CHECKERS[c_type](c_arg)
