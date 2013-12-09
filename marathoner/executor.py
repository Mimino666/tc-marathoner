import os
import pickle
import signal
import socket
import subprocess
import sys
import threading

from marathoner import MARATHONER_PORT
from marathoner.utils.async_reader import AsyncReader
from marathoner.utils.key_press import get_key_press


class Executor(object):
    def __init__(self, project):
        self.project = project
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('127.0.0.1', MARATHONER_PORT))
        self.sock.listen(0)

    def __del__(self):
        self.sock.close()

    def run(self, seed, is_single_test, special_params=''):
        '''Run visualizer on the chosen seed number.
        Return standart output received from visualizer and standard error
        output received from solution.

        @param seed: seed number
        @type seed: int

        @param is_single_test: False, for batch testings
        @type is_single_test: bool

        @param special_params: additional params to pass to visualizer
        @type special_params: string
        '''
        self.is_single_test = is_single_test
        self.solution_stderr, self.visualizer_stdout = [], []

        # start visualizer
        params = self.get_visualizer_params(seed, is_single_test, special_params)
        si = None
        if hasattr(subprocess, 'STARTUPINFO'):
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        visualizer = subprocess.Popen(
            params,
            shell=False,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=si)

        # accept connection from mediator
        conn, addr = self.sock.accept()
        self.socket_reader = conn.makefile('rb')
        self.socket_writer = conn.makefile('wb')
        # initialize mediator
        mediator_settings = {
            'testcase': self.project.testcase,
            'solution': self.project.solution}
        pickle.dump(mediator_settings, self.socket_writer)
        self.socket_writer.flush()
        self.solution_pid = pickle.load(self.socket_reader)

        solution_stderr_reader = AsyncReader(self.socket_reader, self._solution_stderr_cb)
        visualizer_stdout_reader = AsyncReader(visualizer.stdout, self._visualizer_stdout_cb)
        visualizer_stderr_reader = AsyncReader(visualizer.stderr, self._visualizer_stderr_cb)
        solution_stderr_reader.start()
        visualizer_stdout_reader.start()
        visualizer_stderr_reader.start()

        # check for kill signal from user
        self.solution_killed = False
        self.kill_event = threading.Event()
        kill_solution = threading.Thread(target=get_key_press,
                                         args=['q', self.kill_event, self._kill_solution_cb])
        kill_solution.start()

        # wait for readers to finish
        solution_stderr_reader.join()
        visualizer_stdout_reader.join()
        visualizer_stderr_reader.join()

        self.kill_event.set()
        kill_solution.join()

        # close the resources
        self.socket_reader.close()
        self.socket_writer.close()
        conn.close()

        return (self.visualizer_stdout, self.solution_stderr)

    def get_visualizer_params(self, seed, is_single_test, special_params):
        exec_params = [
            'java', '-jar', self.project.visualizer,
            '-exec', 'python ' + self.project.mediator,
            self.project.vis if is_single_test else self.project.novis]
        special_params = special_params.split()
        seed_params = ['-seed', '%s' % seed]

        return exec_params + self.project.params + special_params + seed_params

    def _kill_solution_cb(self):
        self.solution_killed = True
        try:
            os.kill(self.solution_pid, signal.SIGTERM)
        except:
            pass

    def _solution_stderr_cb(self, line):
        '''Read standard error output of solution and store it locally.
        For single tests, output it real-time.
        For multi tests, output only lines starting with "!".
        '''
        line = line.decode('utf-8')
        self.solution_stderr.append(line)
        if self.is_single_test or line[0] == '!':
            sys.stdout.write(line)

    def _visualizer_stdout_cb(self, line):
        '''Read standard output from visualizer and store it locally.
        '''
        self.visualizer_stdout.append(line)

    def _visualizer_stderr_cb(self, line):
        '''Read standard error output from visualizer and output it.
        '''
        sys.stdout.write(line)
