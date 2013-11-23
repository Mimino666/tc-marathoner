import pickle
import socket
import subprocess
import sys

from marathoner import MARATHONER_PORT
from marathoner.async_reader import AsyncReader


class Executor(object):
    def __init__(self, project):
        self.project = project
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', MARATHONER_PORT))
        self.sock.listen(1)

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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=None,
            universal_newlines=True,
            startupinfo=si)

        # accept connection from mediator
        conn, addr = self.sock.accept()
        socket_reader = conn.makefile('r')
        socket_writer = conn.makefile('w')
        # initialize mediator
        mediator_settings = {
            'is_single_test': is_single_test,
            'testcase': self.project.testcase,
            'solution': self.project.solution}
        pickle.dump(mediator_settings, socket_writer)
        socket_writer.flush()

        # read standard error output of solution
        solution_stderr = []
        def solution_stderr_cb(line):
            solution_stderr.append(line)
            if is_single_test or line[0] == '!':
                sys.stdout.write(line)
        solution_stderr_reader = AsyncReader(socket_reader, solution_stderr_cb)
        solution_stderr_reader.start()

        # read standard output from visualizer
        visualizer_stdout = []
        def visualizer_stdout_cb(line):
            visualizer_stdout.append(line)
        visualizer_stdout_reader = AsyncReader(visualizer.stdout, visualizer_stdout_cb)
        visualizer_stdout_reader.start()

        # read standard error output from visualizer
        def visualizer_stderr_cb(line):
            sys.stdout.write(line)
        visualizer_stderr_reader = AsyncReader(visualizer.stderr, visualizer_stderr_cb)
        visualizer_stderr_reader.start()

        # wait for readers to finish
        solution_stderr_reader.join()
        visualizer_stdout_reader.join()
        visualizer_stderr_reader.join()

        # close the resources
        socket_reader.close()
        socket_writer.close()
        conn.close()

        return (visualizer_stdout, solution_stderr)

    def get_visualizer_params(self, seed, is_single_test, special_params):
        exec_params = [
            'java', '-jar', self.project.visualizer,
            '-exec', 'python ' + self.project.mediator,
            self.project.vis if is_single_test else self.project.novis]
        special_params = special_params.split()
        seed_params = ['-seed', str(seed)]

        return exec_params + self.project.params + special_params + seed_params

