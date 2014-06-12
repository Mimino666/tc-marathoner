import re

from six import print_

from marathoner.commands.base import BaseCommand, CommandSyntaxError
from marathoner.tag import Tag
from marathoner.utils.user_input import get_input


class Command(BaseCommand):
    syntax = 'tag create <tag>'
    help = 'create a new tag of your current solution'

    cmd_re = re.compile(r'^\s*tag\s+create\s+(\w+)\s*$', re.IGNORECASE)
    match_re = re.compile(r'^\s*tag\s+create\b', re.IGNORECASE)

    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError
        name = match.group(1)
        tag = self.project.tags.get(name)
        tag_by_hash = self.project.current_tag

        if tag_by_hash and tag_by_hash != tag:
            print_('Current version of your source code already has a different tag: "%s". '
                   'Delete it first.' % tag_by_hash.name)
            return
        elif tag is None:
            print_('Creating new tag "%s".' % name)
            Tag(self.project, name)
        elif tag.source_hash != self.project.source_hash:
            user_input = get_input('Tag "%s" already exists and its source code is different. '
                                   'Should I overwrite it (scores will be kept)? [y/n]' % name, 'yn')
            if user_input == 'n':
                return
            else:
                print_('Overwritting tag "%s" with the new source code.' % name)
                tag.update()
        else:
            print_('Tag "%s" already exists and no change in source code is detected.' % name)

