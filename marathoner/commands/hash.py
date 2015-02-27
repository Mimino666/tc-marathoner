import re

from six import print_

from marathoner.commands.base import BaseCommand, CommandSyntaxError


class Command(BaseCommand):
    syntax = 'hash [<tag>]'
    help = 'output the current or selected tag\'s hash'

    cmd_re = re.compile(r'^\s*hash(?:\s+(\w+))?\s*$', re.IGNORECASE)
    match_re = re.compile(r'^\s*hash\b', re.IGNORECASE)

    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError

        name = match.group(1)
        if name is None:
            print_(self.project.source_hash)
        else:
            tag = self.project.tags.get(name)
            if tag is None:
                print_('Tag "%s" does not exist.' % name)
            else:
                print_(tag.source_hash)

