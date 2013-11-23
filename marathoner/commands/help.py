import re

from marathoner.commands import collect_commands
from marathoner.commands.base import BaseCommand


class Command(BaseCommand):
    syntax = 'help'
    help = 'print help'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.commands = collect_commands()

    cmd_re = re.compile(r'^\s*help\s*$')
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command, vis_params):
        lines = []
        for cmd_name, cmd in self.commands.iteritems():
            lines.append('  %-29s %s' % (cmd.syntax, cmd.help))
        lines.sort()
        for line in lines:
            print line
