import os
import re

from .base import BaseCommand


class Command(BaseCommand):
    syntax = 'clear'
    help = 'clear console window'

    cmd_re = re.compile(r'^\s*clear\s*$')
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command, vis_params):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
