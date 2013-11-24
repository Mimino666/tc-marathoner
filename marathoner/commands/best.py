import re

from marathoner.commands.base import BaseCommand


class Command(BaseCommand):
    syntax = 'best [seed1] [seed2]'
    help = 'print best score for the selected seeds'

    cmd_re = re.compile(r'^\s*best\s*(\d+)?\s*(\d+)?\s*$')
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        def _print(seed):
            seed_str = 'Seed %s:' % seed
            score_str = '%f' % self.project.scores[seed].score
            print '%-10s %s' % (seed_str, score_str)

        match = self.cmd_re.match(command)

        # print all the seeds
        if match.group(1) is None:
            for seed in self.project.scores.sorted_seeds:
                _print(seed)
        # print one specific seed
        elif match.group(2) is None:
            seed = int(match.group(1))
            _print(seed)
        # print interval of seeds
        else:
            seed1 = int(match.group(1))
            seed2 = int(match.group(2))
            if seed2 < seed1:
                print 'Error: seed1 can\'t be larger than seed2!'
                return
            for seed in xrange(seed1, seed2+1):
                _print(seed)
