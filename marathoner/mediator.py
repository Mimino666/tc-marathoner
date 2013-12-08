'''
Mediator is the python program that is actually executed by visualizer,
instead of the user's solution. Mediator executes user's solution as a child
process and redirects all the communication between the visualizer and the
solution.

On background, it communacates with Marathoner through sockets.
This injection hack allows to:
  - export input data from visualizer into testcase file
  - send stderr from solution to Marathoner so it can be outputed in real-time
  - listen for kill-signal from Marathoner to kill the solution
    (when it gets stuck, for example)
'''
import pickle
import shlex
import signal
import socket
import subprocess
import sys

from marathoner import MARATHONER_PORT
from marathoner.utils.async_reader import AsyncReader


class Mediator(object):
    def __init__(self):
        # connect to marathoner
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', MARATHONER_PORT))

        self.socket_reader = self.sock.makefile('r')
        self.socket_writer = self.sock.makefile('w')
        # receive settings
        settings = pickle.load(self.socket_reader)
        self.testcase = settings['testcase']
        self.solution = settings['solution']

        # create the testcase file, if needed
        self.testcase_file = None
        if self.testcase:
            self.testcase_file = open(self.testcase, 'wb')

    def run(self):
        # start solution
        si = None
        if hasattr(subprocess, 'STARTUPINFO'):
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE

        self.solution_proc = subprocess.Popen(
            shlex.split(self.solution),
            shell=False,  # don't set to True, otherwise it is impossible to kill it
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=si)
        pickle.dump(self.solution_proc.pid, self.socket_writer)
        self.socket_writer.flush()

        # setup redirections
        visualizer_input_reader = AsyncReader(sys.stdin, self._visualizer_input_cb)
        visualizer_input_reader.setDaemon(True)
        solution_output_reader = AsyncReader(self.solution_proc.stdout, self._solution_output_cb)
        solution_error_reader = AsyncReader(self.solution_proc.stderr, self._solution_error_cb)
        visualizer_input_reader.start()
        solution_output_reader.start()
        solution_error_reader.start()

        self.solution_proc.wait()
        solution_output_reader.join()
        solution_error_reader.join()

        # return code from solution
        code = self.solution_proc.poll()
        if code:
            signal_name = dict((k, v) for v, k in signal.__dict__.iteritems()
                                      if v.startswith('SIG')) \
                          .get(code, '')
            if signal_name:
                s = '%s (%s)' % (code, signal_name)
            else:
                s = '%s' % code
            msg = 'WARNING: Your solution ended with non-zero return value: %s\n' % s
            self.socket_writer.write(msg)
            self.socket_writer.flush()

        # close the resources
        if self.testcase_file:
            self.testcase_file.close()
        self.socket_reader.close()
        self.socket_writer.close()
        self.sock.close()

    def _visualizer_input_cb(self, line):
        '''Read input from visualizer and redirect it to the solution.
        Also export the input data to testcase file, if available.
        '''
        if self.solution_proc.poll() is None:
            self.solution_proc.stdin.write(line)
            self.solution_proc.stdin.flush()
        if self.testcase_file:
            self.testcase_file.write(line)
            self.testcase_file.flush()

    def _solution_output_cb(self, line):
        '''Read output from the solution and redirect it to the visualizer.
        '''
        sys.stdout.write(line)
        sys.stdout.flush()

    def _solution_error_cb(self, line):
        '''Read standard error output from the solution and redirect it back to
        Marathoner.
        '''
        self.socket_writer.write(line)
        self.socket_writer.flush()


if __name__ == '__main__':
    Mediator().run()
