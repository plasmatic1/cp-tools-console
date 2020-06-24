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

    def _sub_placeholders(self, fmt_str):
        return fmt_str.format(
            src_path=self.src_file,
            src_name=os.path.splitext(self.src_file)[0],
            exe_path=self.exec_file
        )

    def setup(self):
        """
        Does any necessary compilation processes
        """

        if 'compiled' in self.executor_info:
            self.exec_file = self._sub_placeholders(self.executor_info['compiled']['exe_format'])[0]
            sub.call(self._sub_placeholders(self.executor_info['compiled']['command']))
            if not os.path.exists(self.exec_file):
                self.setup_passed = False
        else:
            self.setup_passed = True
            self.exec_file = self.src_file

    def run(self, input):
        """
        Runs the program
        :param input: stdin
        :return: Returns a tuple (CompletedProcess, execution_time)
        """

        start_time = time.time()
        res = sub.run(self.executor_info['command'], text=True, input=input, stdout=sub.PIPE, stderr=sub.PIPE, timeout=float(get_option('timeout')))
        return res, time.time() - start_time

    def cleanup(self):
        """
        Does any cleanup work needed (removing executables primarily)
        """

        if 'compiled' in self.executor_info:
            if os.path.exists(self.exec_file):
                os.remove(self.exec_file)

