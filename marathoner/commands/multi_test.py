import re

from six import print_
from six.moves import xrange

from marathoner.commands.base import BaseCommand


class Command(BaseCommand):
    syntax = '<seed1> <seed2> [<vis params>]'
    help = 'run batch of tests from interval [seed1, seed2]'

    cmd_re = re.compile(r'^\s*(\d+)\s+(\d+)(?:\s+([^\d\s].*))?\s*$', re.IGNORECASE)
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        seed1 = int(match.group(1))
        seed2 = int(match.group(2))
        vis_params = match.group(3) or ''

        if seed2 < seed1:
            print_('Error: seed1 can\'t be larger than seed2!')
            return

        self.project.source_hash_transaction_begin()
        tag = self.project.current_tag
        self.contest.multiple_tests_starting(seed2-seed1+1)
        tests_run = 0
        self.executor.kill_solution_listener_start()
        for seed in xrange(seed1, seed2+1):
            self.contest.one_test_starting(seed)
            current_score, visualizer_stdout, solution_stderr = self.executor.run(seed, False, vis_params)
            if current_score is None:
                print_('Stopping execution...')
                break
            if seed:
                self.project.scores[seed] = current_score
                if tag:
                    tag.scores[seed] = current_score
            self.contest.one_test_ending(seed, visualizer_stdout, solution_stderr,
                                         self.project.scores[seed], current_score)
            tests_run += 1
        self.executor.kill_solution_listener_stop()
        self.project.scores.save()
        if tag:
            tag.scores.save()
        self.contest.multiple_tests_ending(tests_run)
        self.project.source_hash_transaction_end()
