import re

from six import print_

from .tag_one import Command as TagOneCommand
from marathoner.commands.base import BaseCommand, CommandSyntaxError


class Command(BaseCommand):
    syntax = 'cached <tag> <seed> [<vis params>]'
    help = 'run a cached solution of the selected tag'

    cmd_re = re.compile(r'^\s*cached\s+(\w+)(?:\s+(\d+)(?:\s+([^\d\s].*))?)?\s*$', re.IGNORECASE)
    match_re = re.compile(r'^\s*cached\b', re.IGNORECASE)
    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError
        tag_name = match.group(1)
        tag = self.project.tags.get(tag_name)
        if tag is None:
            print_('Tag "%s" doesn\'t exist.' % tag_name)
            return

        if match.group(2) is None:
            command = 'tag %s' % tag_name
            TagOneCommand(self.project, self.executor).handle(command)
        else:
            seed = int(match.group(2))
            vis_params = match.group(3) or ''

            self.project.source_hash_transaction_begin(tag.source_hash)
            self.contest.single_test_starting(seed)
            self.executor.kill_solution_listener_start()
            current_score, visualizer_stdout, solution_stderr = self.executor.run(seed, True, vis_params, tag.source_hash)
            self.executor.kill_solution_listener_stop()
            if current_score is not None:
                self.contest.single_test_ending(seed, visualizer_stdout, solution_stderr,
                                                self.project.scores[seed], current_score)
            self.project.source_hash_transaction_end()
