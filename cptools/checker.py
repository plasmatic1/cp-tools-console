import logging

import cptools.data as data
import cptools.common as common
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
            common.exit()

    def _check(self, input, expected, output):
        res, _, tle = self.exc.run('', self.exc.executor_info['command'] + [input, expected, output])

        def log_case():
            logging.error(f'Case Input (Debug): \n{input.strip()}')
            logging.error(f'Case Output (Debug): \n{output.strip()}')

        if tle:
            log_case()
            logging.error(f'Checker timed out')
            common.exit()
        elif res.returncode or res.stderr:
            log_case()
            logging.error(f'Checker encountered runtime error (exit code: {res.returncode})')
            logging.error(f'STDERR info: {res.stderr}')
            common.exit()

        res.stdout = res.stdout.strip()
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
        common.exit()

    return CHECKERS[c_type](c_arg)
