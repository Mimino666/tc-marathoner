import re

from marathoner.commands.base import BaseCommand


class Command(BaseCommand):
    syntax = '<seed> [<vis params>]'
    help = 'run single test with visualization'

    cmd_re = re.compile(r'^\s*(\d+)(?:\s+([^\d\s].*))?\s*$', re.IGNORECASE)
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        seed = int(match.group(1))
        vis_params = match.group(2) or ''

        self.project.source_hash_transaction_begin()
        tag = self.project.current_tag
        self.contest.single_test_starting(seed)
        self.executor.kill_solution_listener_start()
        current_score, visualizer_stdout, solution_stderr = self.executor.run(seed, True, vis_params)
        self.executor.kill_solution_listener_stop()
        if current_score is not None:
            if seed:
                self.project.scores[seed] = current_score
                self.project.scores.save()
                if tag:
                    tag.scores[seed] = current_score
                    tag.scores.save()
            self.contest.single_test_ending(seed, visualizer_stdout, solution_stderr,
                                            self.project.scores[seed], current_score)
        self.project.source_hash_transaction_end()
