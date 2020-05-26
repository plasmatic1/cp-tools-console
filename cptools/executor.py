import time
import os
import subprocess as sub

from cptools.local_data.data import get_option


def sub_placeholders(arguments, sub_path):
    sub_name = os.path.splitext(sub_path)[0]
    res = []
    for x in arguments:
        if x == '%n':
            res.append(sub_name)
        elif x == '%p':
            res.append(sub_path)
        else:
            res.append(x)
    return res


class Executor:
    def __init__(self, src_file, executor_info):
        self.src_file = src_file
        self.executor_info = executor_info

        self.exec_file, self.setup_passed = None, False

    def setup(self):
        """
        Does any necessary compilation processes
        """

        if 'compiled' in self.executor_info:
            self.exec_file = sub_placeholders([self.executor_info['compiled']['exe_format']], self.src_file)[0]
            sub.call(sub_placeholders(self.executor_info['compiled']['command'], self.src_file))
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

