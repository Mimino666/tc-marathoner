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
        header = [['Tag', 'Created']]
        current_tag = self.project.current_tag
        table = [(('(*) ' if current_tag is tag else '') + tag.name,
                  tag.time_created.strftime('%Y-%m-%d %X'))
                 for tag in itervalues(self.project.tags)]
        if table:
            table.sort(key=itemgetter(1), reverse=True)
            print_table(header, table)
            if current_tag:
                print_('(*) means current active tag')
        else:
            print_('You haven\'t created any tags, yet.')
