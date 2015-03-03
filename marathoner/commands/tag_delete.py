import re

from six import print_

from marathoner.commands.base import BaseCommand, CommandSyntaxError
from marathoner.utils.user_input import get_input


class Command(BaseCommand):
    syntax = 'tag delete <tag>'
    help = 'delete the selected tag'

    cmd_re = re.compile(r'^\s*tag\s+delete\s+(\w+)\s*$', re.IGNORECASE)
    match_re = re.compile(r'^\s*tag\s+delete\b', re.IGNORECASE)

    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError
        tag_name = match.group(1)
        tag = self.project.tags.get(tag_name)

        if tag is None:
            print_('Tag "%s" doesn\'t exist.' % tag_name)
        else:
            user_input = get_input('Are you sure you want to delete tag "%s"? [y/n]' % tag_name, 'yn')
            if user_input == 'y':
                tag.delete()
                print_('Tag "%s" was deleted.' % tag_name)
            else:
                print_('Skipping...')
