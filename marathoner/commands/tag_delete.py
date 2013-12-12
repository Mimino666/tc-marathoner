import re

from six import print_

from marathoner.commands.base import BaseCommand
from marathoner.utils.user_input import get_input


class Command(BaseCommand):
    syntax = 'tag delete <tag>'
    help = 'delete the selected tag'

    cmd_re = re.compile(r'^\s*tag\s+delete\s+(\w+)\s*$', re.IGNORECASE)
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        name = match.group(1)
        tag = self.project.tags.get(name)

        if tag is None:
            print_('Tag "%s" doesn\'t exist.' % name)
        else:
            user_input = get_input('Are you sure you want to delete tag "%s"? [y/n]' % name, 'yn')
            if user_input == 'y':
                tag.delete()
                print_('Tag "%s" was deleted.' % name)
