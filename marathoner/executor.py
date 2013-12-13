import os
import pickle
import signal
import socket
import sys
import threading

from six import print_

from marathoner import MARATHONER_PORT
from marathoner.utils.async_reader import AsyncReader
from marathoner.utils.key_press import get_key_press
from marathoner.utils.ossignal import get_signal_name, install_shutdown_handlers
from marathoner.utils.proc import start_process


class Executor(object):
    def __init__(self, project):
        self.project = project
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        self.sock.bind(('127.0.0.1', MARATHONER_PORT))
        self.sock.listen(1)
        install_shutdown_handlers(self.shutdown_handler)

    def __del__(self):
        self.sock.close()

    def clean(self):
        self.visualizer_proc = None
        self.solution_pid = None
        self.socket_reader = self.socket_writer = None

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
        self.solution_killed = False
        self.solution_crashed = False
        self.solution_stderr, self.visualizer_stdout = [], []

        # start visualizer
        params = self.get_visualizer_params(seed, is_single_test, special_params)
        self.visualizer_proc = start_process(params)

        # accept connection from mediator
        while self.visualizer_proc.poll() is None:
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                pass
            else:
                conn.settimeout(None)
                break
        else:
            code = self.visualizer_proc.poll()
            print_('WARNING: Visualizer ended with non-zero code:', get_signal_name(code))
            self.solution_crashed = True
            self.clean()
            return ([], [])

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
        visualizer_stdout_reader = AsyncReader(self.visualizer_proc.stdout, self._visualizer_stdout_cb)
        visualizer_stderr_reader = AsyncReader(self.visualizer_proc.stderr, self._visualizer_stderr_cb)
        solution_stderr_reader.start()
        visualizer_stdout_reader.start()
        visualizer_stderr_reader.start()

        # wait for readers to finish
        solution_stderr_reader.join()
        visualizer_stdout_reader.join()
        visualizer_stderr_reader.join()

        # close the resources
        self.socket_reader.close()
        self.socket_writer.close()
        conn.close()
        self.clean()

        return (self.visualizer_stdout, self.solution_stderr)

    def shutdown_handler(self, signum, _):
        '''Called when user presses Ctrl+c or some equivalent process killer.
        '''
        install_shutdown_handlers(signal.SIG_IGN)
        print_('Received %s, shutting down gracefully.' % get_signal_name(signum))
        self._kill_solution()
        self.kill_solution_stop()
        try:
            if self.visualizer_proc:
                self.visualizer_proc.kill()
                self.visualizer_proc = None
        except:
            pass
        sys.exit(signum)

    def get_visualizer_params(self, seed, is_single_test, special_params):
        exec_params = [
            'java', '-jar', self.project.visualizer,
            '-exec', 'python ' + self.project.mediator,
            self.project.vis if is_single_test else self.project.novis]
        special_params = special_params.split()
        seed_params = ['-seed', '%s' % seed]
        return exec_params + self.project.params + special_params + seed_params

    def kill_solution_start(self):
        '''Start a new thread listening for kill-solution event (press "Q")
        from user.
        '''
        self.kill_event = threading.Event()
        self.kill_solution = threading.Thread(target=get_key_press,
                                              args=['q', self.kill_event, self._kill_solution])
        self.kill_solution.start()

    def kill_solution_stop(self):
        '''Stop the kill-solution thread.
        '''
        if self.kill_solution:
            self.kill_event.set()
            self.kill_solution.join()
            self.kill_event = None
            self.kill_solution = None

    def _kill_solution(self):
        try:
            if self.solution_pid:
                os.kill(self.solution_pid, signal.SIGTERM)
                self.solution_pid = None
        except:
            pass
        self.solution_killed = True

    def _solution_stderr_cb(self, line):
        '''Read standard error output of solution and store it locally.
        For single tests, output it real-time.
        For multi tests, output only lines starting with "!".
        '''
        line = line.decode('utf-8')
        if line.startswith('!WARNING:'):
            self.solution_crashed = True
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
