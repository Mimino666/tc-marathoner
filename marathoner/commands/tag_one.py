import re

from six import print_

from marathoner.commands.base import BaseCommand
from marathoner.scores import Score
from marathoner.utils.print_table import print_table


class Command(BaseCommand):
    syntax = 'tag <tag>'
    help = 'print scores of selected tag'

    cmd_re = re.compile(r'^\s*tags?\s+(\w+)\s*$', re.IGNORECASE)
    def is_match(self, command):
        match = self.cmd_re.match(command)
        return match and match.group(1) not in ('create', 'delete')

    def handle(self, command):
        tag_name = self.cmd_re.match(command).group(1)
        tag = self.project.tags.get(tag_name)
        if tag is None:
            print_('Tag "%s" doesn\'t exist.' % tag_name)
            return

        # prepare the data for table
        header = [['Seed', 'Score', 'Best', 'Relative', 'Run time']]
        table = []
        zero_seeds = []
        score_sum = 0.0

        for seed in sorted(tag.scores.seeds):
            best_score = self.project.scores[seed]
            current_score = tag.scores[seed]
            relative = Score.relative_score(
                self.project.maximize, current_score, best_score)
            score_sum += relative
            if not current_score.score:
                zero_seeds.append(seed)
            table.append([
                seed,
                '%.2f' % current_score.score,
                '%.2f' % best_score.score,
                '%.3f' % relative,
                '%.2f' % current_score.run_time])

        print_table(header, table, header)
        print_()
        num_tests = len(tag.scores)
        print_('Relative score of "%s" tag on %s tests: %.5f' % (tag_name, num_tests, score_sum))
        if num_tests:
            print_('Average relative score: %.5f' % (score_sum / num_tests))
        if zero_seeds:
            print_('You have scored zero points on %s seeds. Here are some of the seeds: %s' %
                   (len(zero_seeds), zero_seeds[:10]))
