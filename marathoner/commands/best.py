import re

from six import print_
from six.moves import xrange

from marathoner.commands.base import BaseCommand, CommandSyntaxError
from marathoner.utils.print_table import print_table


class Command(BaseCommand):
    syntax = 'best [<seed1>] [<seed2>]'
    help = 'print best score for the selected seeds'

    cmd_re = re.compile(r'^\s*best(?:\s+(\d+)(?:\s+(\d+))?)?\s*$', re.IGNORECASE)
    match_re = re.compile(r'\s*best\b', re.IGNORECASE)

    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        header = [['Seed', 'Score', 'Run time']]
        table = []
        def add_seed(seed):
            score = self.project.scores[seed]
            table.append([seed, '%.2f' % score.score, '%.2f' % score.run_time])

        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError

        # print all the seeds
        if match.group(1) is None:
            for seed in sorted(self.project.scores.seeds):
                add_seed(seed)
        # print one specific seed
        elif match.group(2) is None:
            seed = int(match.group(1))
            add_seed(seed)
        # print interval of seeds
        else:
            seed1 = int(match.group(1))
            seed2 = int(match.group(2))
            if seed2 < seed1:
                print_('Error: seed1 can\'t be larger than seed2!')
                return
            for seed in xrange(seed1, seed2+1):
                add_seed(seed)
        print_table(header, table, header)
