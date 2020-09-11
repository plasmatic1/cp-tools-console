import logging
import time
import os
import subprocess as sub
import cptools.util as cptools_util

from cptools.data import get_option, get_executors, get_executor


# Returns None if no executor was found
def default_executor_name(src_path):
    ext = os.path.splitext(src_path)[1][1:]  # Remove the dot
    for exc_name in get_executors():
        exc = get_executor(exc_name)
        if ext in exc['ext']:
            return exc_name
    return None


class Executor:
    def __init__(self, src_file, executor_info):
        self.src_file = src_file
        self.executor_info = executor_info

        self.exec_file, self.setup_passed = None, False

        # Auxillary info
        if self.is_compiled():
            self.compile_command = ' '.join(self.executor_info['compiled']['command'])
        else:
            self.compile_command = None

    def _sub_placeholder(self, fmt_str):
        return fmt_str.format(
            src_path=self.src_file,
            src_name=os.path.splitext(self.src_file)[0],
            exe_path=self.exec_file
        )

    def _sub_placeholder_list(self, fmt_list):
        return [self._sub_placeholder(fmt_name) for fmt_name in fmt_list]

    def is_compiled(self):
        return 'compiled' in self.executor_info

    def setup(self):
        """
        Does any necessary compilation processes
        :return: The compilation time (float) in seconds
        """

        if self.is_compiled():
            self.exec_file = self._sub_placeholder(self.executor_info['compiled']['exe_format'])
            ctime = time.time()
            sub.call(self._sub_placeholder_list(self.executor_info['compiled']['command']))
            elapsed = time.time() - ctime
            self.setup_passed = os.path.exists(self.exec_file)
        else:
            self.setup_passed = True
            self.exec_file = self.src_file
            elapsed = -1

        return elapsed

    def run(self, input, command=None, *args):
        """
        Runs the program
        :param input: stdin
        :param command: The command to run (optional and generally only for internals)
        :param args: Any extra process arguments to specify
        :return: Returns a tuple (CompletedProcess, execution_time, TLE)
        """

        start_time = time.time()
        try:
            res = sub.run(self._sub_placeholder_list(command or self.executor_info['command']) + list(args), text=True, input=input,
                          stdout=sub.PIPE, stderr=sub.PIPE, timeout=float(get_option('timeout')))
            return res, time.time() - start_time, False
        except sub.TimeoutExpired as e:
            # Sometimes returned as str, sometimes as bytes
            stdout = str(e.stdout, 'utf8') if type(e.stdout) == bytes else (e.stdout or '')  # If stream output is None
            stderr = str(e.stderr, 'utf8') if type(e.stderr) == bytes else (e.stderr or '')  # "
            return sub.CompletedProcess([], -1, stdout, stderr), time.time() - start_time, True

    def cleanup(self):
        """
        Does any cleanup work needed (removing executables primarily)
        """

        if 'compiled' in self.executor_info:
            if os.path.exists(self.exec_file):
                try:
                    os.unlink(self.exec_file)
                except PermissionError as e:
                    logging.warning(f'Could not remove executable (Error: {e})')
                    logging.warning('The executable will not be removed (you can remove it manually)')


def compile_source_file(src_file, executor=None):
    """
    Compiles a source file with the specified executor (if the language is compiled.  If it's interpreted then it simply returns the executor for the source file.
    If any errors occur, they'll be printed to STDOUT and the process will be halted.  Note that if no executor is specified, then the default executor for the source
    file will be used
    :param src_file: The source file
    :param executor: The executor, or None if the default executor for the source file should be used.
    :return: The executor for the source file, with all setup processes (compilation) completed
    """

    exc_name = executor or default_executor_name(src_file)
    logging.debug(f'Using executor {exc_name}')

    # Compile
    try:
        exc = Executor(src_file, get_executor(exc_name))
    except ValueError as e:
        logging.error(e)
        cptools_util.exit()

    if not os.path.exists(src_file):
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

    return exc
