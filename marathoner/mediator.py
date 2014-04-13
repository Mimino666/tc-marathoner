'''
Mediator is a python script that gets executed by visualizer,
instead of the user's solution. Mediator executes user's solution as a child
process and redirects all the communication between the visualizer and the
solution. On background, it communacates with Marathoner through sockets.

This injection allows to:
  - export input data from visualizer into testcase file
  - send stderr from solution to Marathoner so it can be outputed in real-time
  - better handling of crash of user's solution
  - killing of stuck user's solution (by pressing "q")
'''
import pickle
import socket
import sys
import time

from marathoner import MARATHONER_PORT, MARATHONER_END_OF_OUTPUT
from marathoner.utils.async_reader import AsyncReader
from marathoner.utils.proc import start_process


class Mediator(object):
    def __init__(self):
        # connect to marathoner
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', MARATHONER_PORT))

        self.socket_reader = self.sock.makefile('rb')
        self.socket_writer = self.sock.makefile('wb')
        # receive settings
        settings = pickle.load(self.socket_reader)
        self.testcase = settings['testcase']
        self.solution = settings['solution']

        # create the testcase file, if needed
        self.testcase_file = None
        if self.testcase:
            self.testcase_file = open(self.testcase, 'w')
        # lines received from the solution (later redirected to visualizer)
        self.solution_line_buffer = []

    def run(self):
        self.solution_proc = start_process(self.solution)
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
        start_time = time.time()
        self.solution_proc.wait()
        end_time = time.time()
        solution_output_reader.join()
        solution_error_reader.join()

        # signalize end of stderr output
        self.socket_writer.write(MARATHONER_END_OF_OUTPUT.encode('utf-8'))
        # raw run time
        pickle.dump(end_time-start_time, self.socket_writer)
        # exit code of solution
        pickle.dump(self.solution_proc.poll(), self.socket_writer)
        self.socket_writer.flush()

        # close the resources
        if self.testcase_file:
            self.testcase_file.close()
        self.socket_reader.close()
        self.socket_writer.close()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

        # write output to visualizer
        for line in self.solution_line_buffer:
            sys.stdout.write(line)
        sys.stdout.flush()

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
        '''Read output from the solution and store it for later use.
        '''
        self.solution_line_buffer.append(line)

    def _solution_error_cb(self, line):
        '''Read standard error output from the solution and redirect it back to
        Marathoner.
        '''
        self.socket_writer.write(line.encode('utf-8'))
        self.socket_writer.flush()


if __name__ == '__main__':
    Mediator().run()
