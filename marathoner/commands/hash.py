import re

from six import print_

from marathoner.commands.base import BaseCommand, CommandSyntaxError


class Command(BaseCommand):
    syntax = 'hash [<tag>]'
    help = 'output the hash of the current or selected tag'

    cmd_re = re.compile(r'^\s*hash(?:\s+(\w+))?\s*$', re.IGNORECASE)
    match_re = re.compile(r'^\s*hash\b', re.IGNORECASE)

    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError

        tag_name = match.group(1)
        if tag_name is None:
            print_(self.project.source_hash)
        else:
            tag = self.project.tags.get(tag_name)
            if tag is None:
                print_('Tag "%s" does not exist.' % tag_name)
            else:
                print_(tag.source_hash)

