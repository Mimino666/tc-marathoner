import re
import sys

from .base import BaseCommand


class Command(BaseCommand):
    syntax = 'quit'
    help = 'quit marathoner'

    cmd_re = re.compile(r'^\s*(quit|exit)\s*$')
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command, vis_params):
        print 'Bye bye...'
        sys.exit(0)
