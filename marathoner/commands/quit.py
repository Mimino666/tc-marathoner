import re
import sys

from marathoner.commands.base import BaseCommand


class Command(BaseCommand):
    syntax = 'quit'
    help = 'quit marathoner'

    cmd_re = re.compile(r'^\s*(quit|exit)\s*$')
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        print 'Bye bye...'
        sys.exit(0)