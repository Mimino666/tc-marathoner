from datetime import datetime
import os
import pickle
import re
import shlex
import signal
import socket
import sys
import threading

from six import print_

from marathoner import MARATHONER_PORT, MARATHONER_END_OF_OUTPUT
from marathoner.scores import Score
from marathoner.utils.async_reader import AsyncReader
from marathoner.utils.key_press import get_key_press
from marathoner.utils.ossignal import get_signal_name, install_shutdown_handlers
from marathoner.utils.proc import start_process


class ExecutorError(Exception):
    pass


class Executor(object):
    run_time_re = re.compile(r'^\s*Run\s+time\s*=\s*(\d+(?:[.,]\d+)?)\s*$')

    def __init__(self, project):
        self.project = project
        self.contest = project.contest
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        self.sock.bind(('127.0.0.1', MARATHONER_PORT))
        self.sock.listen(1)
        install_shutdown_handlers(self.shutdown_handler)

    def __del__(self):
        self.sock.close()

    def run(self, seed, is_single_test, special_params='', source_hash=None):
        '''Run visualizer on the chosen seed number.
        Returns extracted score, standard output received from visualizer and
        standard error output received from solution.

        @param seed: seed number
        @type seed: int

        @param is_single_test: False, for batch testings
        @type is_single_test: bool

        @param special_params: additional params to pass to visualizer
        @type special_params: string

        @param source_hash: use it to force running a cached solution
        @type source_hash: string (source hash) or None
        '''
        self.is_single_test = is_single_test
        self.solution_killed = False
        self.solution_crashed = False
        self.run_time = None
        self.solution_stderr, self.visualizer_stdout = [], []

        if self.project.cache and seed:
            cache_stdout_fn = self.project.get_cache_stdout_fn(seed, source_hash)
            cache_stderr_fn = self.project.get_cache_stderr_fn(seed, source_hash)
            use_cache = (os.path.exists(cache_stdout_fn) and
                         os.path.exists(cache_stderr_fn))
            if source_hash and not use_cache:
                print_('WARNING: Cached solution for seed %s does not exist.' % seed)
                self.solution_crashed = True
                return (None, [], [])
        else:
            cache_stdout_fn = cache_stderr_fn = None
            use_cache = False

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
            return (None, [], [])

        self.socket_reader = conn.makefile('rb')
        self.socket_writer = conn.makefile('wb')
        # initialize mediator
        mediator_settings = {
            'testcase': self.project.testcase,
            'solution': self.project.solution,
            'use_cache': use_cache,
            'cache_stdout_fn': cache_stdout_fn,
            'cache_stderr_fn': cache_stderr_fn,
            'visualizer': os.path.basename(self.project.visualizer)}
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

        try:
            raw_run_time = pickle.load(self.socket_reader)
            exit_code = pickle.load(self.socket_reader)
        except EOFError:
            raw_run_time = 0.0
            exit_code = -1
        if self.run_time is None:
            self.run_time = raw_run_time
        if exit_code and not self.solution_killed:
            print_('WARNING: Your solution ended with non-zero code: %s' % get_signal_name(exit_code))
            self.solution_crashed = True

        # close the resources
        self.socket_reader.close()
        self.socket_writer.close()
        conn.close()

        # write to log
        with open(self.project.data_path('log'), 'a') as run_log:
            run_log.write('%s Seed: %s Run time: %s Hash: %s Tag: %s Failed: %s From cache: %s\n' %
                (datetime.now(), seed, self.run_time,
                 source_hash or self.project.source_hash,
                 self.project.current_tag,
                 self.solution_crashed or self.solution_killed, use_cache))

        if self.solution_crashed or self.solution_killed:
            # delete partially filled cache
            if self.project.cache and not use_cache:
                if os.path.exists(cache_stdout_fn):
                    os.remove(cache_stdout_fn)
                if os.path.exists(cache_stderr_fn):
                    os.remove(cache_stderr_fn)
            return (None, self.visualizer_stdout, self.solution_stderr)
        else:
            raw_score = self.contest.extract_score(self.visualizer_stdout, self.solution_stderr)
            if raw_score is None:
                return (None, self.visualizer_stdout, self.solution_stderr)
            score = Score(seed, raw_score, self.run_time)
            return (score, self.visualizer_stdout, self.solution_stderr)

    def shutdown_handler(self, signum, _):
        '''Called when user presses Ctrl+c or some equivalent process killer.
        '''
        install_shutdown_handlers(signal.SIG_IGN)
        print_('Received %s, shutting down gracefully.' % get_signal_name(signum))
        self._kill_solution()
        self.kill_solution_listener_stop()
        try:
            self.visualizer_proc.kill()
        except:
            pass
        sys.exit(signum)

    def get_visualizer_params(self, seed, is_single_test, special_params):
        exec_params = [
            'java', '-jar', self.project.visualizer,
            '-exec', 'python "%s"' % self.project.mediator,
            self.project.vis if is_single_test else self.project.novis]
        special_params = shlex.split(special_params)
        seed_params = ['-seed', '%s' % seed]
        params = exec_params + self.project.params + special_params + seed_params
        params = [p for p in params if p]  # clean params of empty values
        return params

    def kill_solution_listener_start(self):
        '''Start a new thread listening for kill-solution event (press "Q")
        from user.
        '''
        self.stop_listener_event = threading.Event()
        self.listener_thread = threading.Thread(target=get_key_press,
                                                args=['q', self.stop_listener_event, self._kill_solution])
        self.listener_thread.start()

    def kill_solution_listener_stop(self):
        '''Stop the kill-solution thread.
        '''
        if self.listener_thread:
            self.stop_listener_event.set()
            self.listener_thread.join()
            self.stop_listener_event = None
            self.listener_thread = None

    def _kill_solution(self):
        try:
            if self.solution_pid:
                os.kill(self.solution_pid, signal.SIGTERM)
        except:
            pass
        self.solution_killed = True

    def _solution_stderr_cb(self, line):
        '''Read standard error output of solution and store it locally.
        For single tests, output it real-time.
        For multi tests, output only lines starting with "!".
        '''
        line = line.decode('utf-8')
        if line == MARATHONER_END_OF_OUTPUT:
            return True
        # try to parse run time received from user
        run_time_match = self.run_time_re.match(line)
        if run_time_match:
            self.run_time = float(run_time_match.group(1))
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
