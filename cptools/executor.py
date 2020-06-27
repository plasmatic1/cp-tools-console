import time
import os
import subprocess as sub

from cptools.data import get_option, get_executors_list, get_executor


# Returns None if no executor was found
def default_executor_name(src_path):
    ext = os.path.splitext(src_path)[1][1:]  # Remove the dot
    for exc_name in get_executors_list():
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
        self.compile_command = ' '.join(self.executor_info['compiled']['command'])

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
        """

        if 'compiled' in self.executor_info:
            self.exec_file = self._sub_placeholder(self.executor_info['compiled']['exe_format'])
            sub.call(self._sub_placeholder_list(self.executor_info['compiled']['command']))
            self.setup_passed = os.path.exists(self.exec_file)
        else:
            self.setup_passed = True
            self.exec_file = self.src_file

    def run(self, input, command=None):
        """
        Runs the program
        :param input: stdin
        :param command: The command to run (optional and generally only for internals)
        :return: Returns a tuple (CompletedProcess, execution_time, TLE)
        """

        start_time = time.time()
        try:
            res = sub.run(self._sub_placeholder_list(command or self.executor_info['command']), text=True, input=input,
                          stdout=sub.PIPE, stderr=sub.PIPE, timeout=float(get_option('timeout')))
            return res, time.time() - start_time, False
        except sub.TimeoutExpired as e:
            return sub.CompletedProcess([], -1, e.stdout, e.stderr), time.time() - start_time, True

    def cleanup(self):
        """
        Does any cleanup work needed (removing executables primarily)
        """

        if 'compiled' in self.executor_info:
            if os.path.exists(self.exec_file):
                os.remove(self.exec_file)

