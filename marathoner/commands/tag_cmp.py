import re

from six import print_
from six.moves import reduce

from marathoner.commands.base import BaseCommand
from marathoner.scores import Score
from marathoner.utils.print_table import print_table


class Command(BaseCommand):
    syntax = 'tag cmp <tag1> <tag2> ...'
    help = 'compare the scores of selected tags'

    cmd_re = re.compile(r'^\s*tag\s+cmp\s+(\w+(?:\s+\w+)*)\s*$', re.IGNORECASE)
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        tags = []
        seeds = None
        for name in match.group(1).split():
            tag = self.project.tags.get(name)
            if tag is None:
                print_('Tag "%s" doesn\'t exist.' % name)
                return
            tags.append(tag)
            if seeds is None:
                seeds = set(tag.scores.seeds)
            else:
                seeds &= set(tag.scores.seeds)
        if not seeds:
            print_('Selected tags have no seeds in common.')
            return

        # prepare the data for table:
        #   Seed | <tag1> | <tag2> | ... | Best score
        header = [['Seed'] + [tag.name for tag in tags] + ['Best']]
        table = []
        relative_score = [0] * len(tags)
        num_absolute_best = [0] * len(tags)
        num_best = [0] * len(tags)

        for seed in sorted(seeds):
            best_score = self.project.scores[seed]
            row = []
            local_best_score = reduce(
                lambda x, tag: Score.better(self.project.maximize, x, tag.scores[seed]),
                tags,
                Score(seed, 0))
            for i, tag in enumerate(tags):
                current_score = tag.scores[seed]
                relative_score[i] += Score.relative_score(
                    self.project.maximize, current_score, best_score)
                if current_score.score == best_score.score:
                    row.append('(+) %.2f' % current_score.score)
                    num_absolute_best[i] += 1
                    num_best[i] += 1
                elif current_score.score == local_best_score.score:
                    row.append('(*) %.2f' % current_score.score)
                    num_best[i] += 1
                else:
                    row.append('%.2f' % current_score.score)
            table.append([seed] + row + ['%.2f' % best_score.score])
        footer = [
            ['Relative'] + ['%.5f' % x for x in relative_score] + [len(seeds)],
            ['# (*)'] + num_best + ['/'],
            ['# (+)'] + num_absolute_best + ['/'],
        ]

        print_table(header, table, footer)
        print_()
        print_('(*) means the best score among the selected tags')
        print_('(+) means the absolute best score')
