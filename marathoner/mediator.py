'''
Mediator is a man-in-the-middle app between the visualizer and the
solution created by the competitor.

Its main purpose is to redirect inputs and outputs between the visualizer and
the solution, so that everything works as expected.

Its secondary purpose is to store the input received from the visualizer to
the file, send the standard error output from solution to Marathoner and
listen for a kill-signal in a case when user decided to kill the
solution (by pressing 'Q').
'''
import pickle
import socket
import subprocess
import sys

from marathoner import MARATHONER_PORT
from marathoner.async_reader import AsyncReader


class Mediator(object):
    def __init__(self):
        # connect to marathoner
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', MARATHONER_PORT))

        self.socket_reader = self.sock.makefile('r')
        self.socket_writer = self.sock.makefile('w')
        # receive project settings
        self.is_single_test, self.project = pickle.load(self.socket_reader)

        # create the testcase file, if needed
        self.testcase_file = None
        if self.is_single_test and self.project.testcase:
            self.testcase_file = open(self.project.testcase, 'wb')

    def run(self):
        # start solution
        si = None
        if hasattr(subprocess, 'STARTUPINFO'):
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE

        self.solution = subprocess.Popen(
            self.project.solution,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=None,
            universal_newlines=True,
            startupinfo=si)

        # setup redirections
        visualizer_input_reader = AsyncReader(sys.stdin, self._visualizer_input_cb)
        visualizer_input_reader.setDaemon(True)
        solution_output_reader = AsyncReader(self.solution.stdout, self._solution_output_cb)
        solution_error_reader = AsyncReader(self.solution.stderr, self._solution_error_db)

        visualizer_input_reader.start()
        solution_output_reader.start()
        solution_error_reader.start()

        solution_output_reader.join()
        solution_error_reader.join()

        # close the resources
        if self.testcase_file:
            self.testcase_file.close()
        self.socket_reader.close()
        self.socket_writer.close()
        self.sock.close()

    def _visualizer_input_cb(self, line):
        '''Read input from visualizer and redirect it to the solution.
        If needed, write the input to the separate file.
        '''
        if self.solution.poll() is None:
            self.solution.stdin.write(line)
            self.solution.stdin.flush()
        if self.testcase_file:
            self.testcase_file.write(line)
            self.testcase_file.flush()

    def _solution_output_cb(self, line):
        '''Read output from the solution and redirect it to the visualizer.
        '''
        sys.stdout.write(line)
        sys.stdout.flush()

    def _solution_error_db(self, line):
        '''Read standard error output from the solution and redirect it back to
        Marathoner.
        '''
        self.socket_writer.write(line)
        self.socket_writer.flush()


if __name__ == '__main__':
    Mediator().run()
