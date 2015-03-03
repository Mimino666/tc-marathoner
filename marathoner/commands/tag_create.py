import re

from six import print_

from marathoner.commands.base import BaseCommand, CommandSyntaxError
from marathoner.tag import Tag
from marathoner.utils.user_input import get_input


class Command(BaseCommand):
    syntax = 'tag create <tag>'
    help = 'tag the current solution with name <tag>'

    cmd_re = re.compile(r'^\s*tag\s+create\s+(\w+)\s*$', re.IGNORECASE)
    match_re = re.compile(r'^\s*tag\s+create\b', re.IGNORECASE)

    def is_match(self, command):
        return self.match_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        if not match:
            raise CommandSyntaxError
        tag_name = match.group(1)
        tag = self.project.tags.get(tag_name)
        tag_by_hash = self.project.current_tag

        if tag_by_hash and tag_by_hash != tag:
            print_('Current version of your source code already has a tag "%(tag)s". '
                   'Delete tag "%(tag)s" before proceeding further.' % {'tag': tag_by_hash.name})
            return
        elif tag is None:
            print_('Creating new tag "%s".' % tag_name)
            Tag(self.project, tag_name)
        elif tag.source_hash != self.project.source_hash:
            user_input = get_input('Tag "%s" already exists and is associated with a different source code. '
                                   'Should I overwrite it (scores will be kept)? [y/n]' % tag_name, 'yn')
            if user_input == 'y':
                print_('Overwritting tag "%s" with the new source code.' % tag_name)
                tag.update()
            else:
                print_('Skipping...')
        else:
            print_('Tag "%s" already exists and no change in source code is detected.' % tag_name)

