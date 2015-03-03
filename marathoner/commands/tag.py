from operator import itemgetter
import re

from six import print_, itervalues

from marathoner.commands.base import BaseCommand
from marathoner.utils.print_table import print_table


class Command(BaseCommand):
    syntax = 'tag'
    help = 'print list of existing tags'

    cmd_re = re.compile(r'^\s*tags?\s*$', re.IGNORECASE)
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        header = [['Tag', 'Seeds', 'Avg. score', 'Created']]
        current_tag = self.project.current_tag
        table = []
        best_score = 0.0
        for tag in itervalues(self.project.tags):
            avg_score = tag.get_avg_relative_score()
            best_score = max(best_score, avg_score)
            row = [
                ('(*) ' if current_tag is tag else '') + tag.name,
                len(tag.scores),
                avg_score,
                tag.time_created.strftime('%Y-%m-%d %X')]
            table.append(row)

        # format avg scores
        for row in table:
            avg_score = row[2]
            if avg_score == best_score:
                row[2] = '(!) %.5f' % avg_score
            else:
                row[2] = '%.5f' % avg_score

        if table:
            table.sort(key=itemgetter(3))
            print_table(header, table)
            print_()
            if current_tag:
                print_('(*) means current active tag')
            print_('(!) means the best average relative score')
        else:
            print_('You haven\'t created any tags, yet.')
