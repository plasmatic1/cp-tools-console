import subprocess as sub
import unittest
import re
import os
import os.path as path
from textwrap import dedent

# 7-bit and 8-bit C1 ANSI sequences
ANSI_ESCAPE_REGEX = re.compile(br'''
    (?: # either 7-bit C1, two bytes, ESC Fe (omitting CSI)
        \x1B
        [@-Z\\-_]
    |   # or a single 8-bit byte Fe (omitting CSI)
        [\x80-\x9A\x9C-\x9F]
    |   # or CSI + control codes
        (?: # 7-bit CSI, ESC [ 
            \x1B\[
        |   # 8-bit CSI, 9B
            \x9B
        )
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


def remove_ansi_escapes(s):
    return str(ANSI_ESCAPE_REGEX.sub(b'', bytes(s, 'utf8')), 'utf8')


# Note: CWD should be set to <repository location>/cptools/tests
def get_output(cmd, proc_in=''):
    res = sub.run(cmd, stdout=sub.PIPE, stderr=sub.STDOUT, text=True, input=proc_in)
    return remove_ansi_escapes(res.stdout)


LOG_TIMEHOST_REGEX = r'\[\d+:\d+:\d+\/\w+]'
RUN_REGEX = f'''{LOG_TIMEHOST_REGEX} INFO Running [\\w.]+ using cases from [\\w.]+
{LOG_TIMEHOST_REGEX} INFO Compiling...
{LOG_TIMEHOST_REGEX} INFO Loading test data...

'''
TIME_REGEX = r'\[\d+\.\d{3}s\]'


class RegexBasedTest(unittest.TestCase):
    def _check_run(self, out, reg):
        self.assertRegex(out, dedent(reg).strip())


TEST_AC_WA_REGEX = f'''
    Case #0: AC {TIME_REGEX}
    Case #1: WA {TIME_REGEX}
    == Input ==
    6 7

    == Output ==
    13

    == Expected Output ==
    12

    Case #2: AC {TIME_REGEX}
    Case #3: AC {TIME_REGEX}
    '''

class VerdictTests(RegexBasedTest):
    def test_ac_wa(self):
        out = get_output(['cptools-run', 'test_aplusb.yml', 'test_aplusb.cpp'])
        self._check_run(out, TEST_AC_WA_REGEX)

    def test_tle(self):
        out = get_output(['cptools-run', 'test_aplusb.yml', 'test_aplusb_tle.cpp'])
        self._check_run(out, f'''
        Case #0: TLE \\[>1\\.000s\\]
        == Input ==
        3 4

        == Output ==
        tle!

        == Expected Output ==
        7

        Case #1: WA {TIME_REGEX}
        == Input ==
        6 7

        == Output ==
        13

        == Expected Output ==
        12

        Case #2: AC {TIME_REGEX}
        Case #3: AC {TIME_REGEX}
        ''')

    def test_rte(self):
        out = get_output(['cptools-run', 'test_aplusb.yml', 'test_aplusb_rte.cpp'])
        self._check_run(out, rf'''
        Case #0: RTE \(Exit Code: \d+\) {TIME_REGEX}
        == Input ==
        3 4

        == Output ==

        == Expected Output ==
        7

        Case #1: RTE \(Exit Code: \d+\) {TIME_REGEX}
        == Input ==
        6 7

        == Output ==

        == Expected Output ==
        12

        Case #2: RTE \(Exit Code: \d+\) {TIME_REGEX}
        == Input ==
        3 5

        == Output ==

        == Expected Output ==
        8

        Case #3: RTE \(Exit Code: 3\) {TIME_REGEX}
        == Errors ==
        Assertion failed!

        Program: E:\\repos\\cp-tools-console\\cptools\\tests\\test_aplusb_rte.exe
        File: test_aplusb_rte.cpp, Line 8

        Expression: a\[0\] != 1

        == Input ==
        1 1

        == Output ==

        == Expected Output ==
        2
        ''')

    def test_ce(self):
        out = get_output(['cptools-run', 'test_aplusb.yml', 'test_aplusb_rte.cpp', '-e', 'cpp-debug'])
        self._check_run(out, rf'''
        {LOG_TIMEHOST_REGEX} INFO Running test_aplusb_rte.cpp using cases from test_aplusb.yml
        {LOG_TIMEHOST_REGEX} INFO Compiling...
        .+
        .+
        .+ error: ld returned 1 exit status
        {LOG_TIMEHOST_REGEX} ERROR Compile failed!
        ''')


class InvalidConfigurationTests(RegexBasedTest):
    def test_invalid_config(self):
        old_dir = os.getcwd()
        os.chdir(path.join(old_dir, 'err_tests', 'invalid_config'))
        out = get_output(['cptools-run', r'..\..\test_aplusb.yml', r'..\..\test_aplusb.cpp'])
        self._check_run(out,
                        fr'{LOG_TIMEHOST_REGEX} ERROR Error while parsing config: Invalid value "123" for config key "default_checker" \(expected string\)')
        os.chdir(old_dir)

    def test_invalid_executor(self):
        old_dir = os.getcwd()
        os.chdir(path.join(old_dir, 'err_tests', 'invalid_executor'))
        out = get_output(['cptools-run', r'..\..\test_aplusb.yml', r'..\..\test_aplusb.cpp'])
        self._check_run(out, fr'{LOG_TIMEHOST_REGEX} ERROR Error while parsing executors: Invalid value'
            r' "\[1, \'-O0\', \'-DLOCAL\', \'-o\', \'\{exe_path\}\', \'\{src_path\}\'\]" for config key "command"'
            r' in path "cpp.compiled" \(expected list of strings\)')
        os.chdir(old_dir)


class LanguageTests(RegexBasedTest):
    def test_py(self):
        out = get_output(['cptools-run', 'test_aplusb.yml', 'test_aplusb.py'])
        self._check_run(out, TEST_AC_WA_REGEX)


class OptionTests(RegexBasedTest):
    def test_verbose(self):
        out = get_output(['cptools-run', 'test_aplusb.yml', 'test_aplusb.cpp', '--verbose'])
        self._check_run(out, rf'''
            {LOG_TIMEHOST_REGEX} DEBUG Working directory: {re.escape(os.getcwd())}
            {LOG_TIMEHOST_REGEX} DEBUG Timeout: 1\.0
            {LOG_TIMEHOST_REGEX} DEBUG Display Character Limit: 1000000
            {LOG_TIMEHOST_REGEX} DEBUG Using executor cpp
            {LOG_TIMEHOST_REGEX} DEBUG Compile command: {re.escape(r"g++ -O0 -DLOCAL -o {exe_path} {src_path}")}
            {LOG_TIMEHOST_REGEX} INFO Compiling\.\.\.
            {LOG_TIMEHOST_REGEX} DEBUG Compile time: \d+\.\d{{3}}s
        ''')


class CheckerTests(RegexBasedTest):
    def test_float_checker(self):
        out = get_output(['cptools-run', 'test_float.yml', 'test_float.py'])
        self._check_run(out, rf'''
        Case #0: AC {TIME_REGEX}
        Case #1: WA {TIME_REGEX}
        == Input ==
        3 0\.1

        == Output ==
        3\.1

        == Expected Output ==
        3

        Case #2: WA {TIME_REGEX}
        == Input ==
        3 1

        == Output ==
        4\.0

        == Expected Output ==
        3

        Case #3: WA \(could not convert string to float: 'not'\) {TIME_REGEX}
        == Input ==
        3 -1

        == Output ==
        not a float!
        2\.0

        == Expected Output ==
        3
        ''')

    def test_custom_checker(self):
        out = get_output(['cptools-run', 'test_aplusb_custom_checker.yml', 'test_aplusb.cpp'])
        self._check_run(out, rf'''
        Case #0: AC {TIME_REGEX}
        Case #1: WA \(diff 1, wanted 12, got 13\) {TIME_REGEX}
        == Input ==
        6 7

        == Output ==
        13

        == Expected Output ==
        12

        Case #2: AC {TIME_REGEX}
        Case #3: AC {TIME_REGEX}
        ''')


class BugTests(RegexBasedTest):
    # Just check if it terminates normally
    def test_unprintable_chars(self):
        res = sub.run(['cptools-run', 'test_aplusb.yml', 'test_aplusb_unprintable.cpp'], stdout=sub.PIPE, stderr=sub.PIPE)
        self.assertEqual(res.returncode, 0)


if __name__ == '__main__':
    unittest.main()
