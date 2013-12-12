from datetime import datetime
import os
from os import path
from shutil import copyfile

from marathoner.scores import Scores


class Tag(object):
    def __init__(self, project, name, create_new=False):
        self.project = project
        self.name = name
        self.scores_filename = path.join(project.tags_dir, name+'.score')
        self.scores = Scores(project, self.scores_filename)
        self.source_filename = path.join(project.tags_dir, name+project.source_ext)
        if create_new:
            copyfile(self.project.source, self.source_filename)

        if path.exists(self.source_filename):
            self.source_hash = project.hash_of_file(self.source_filename)
        else:
            from marathoner.project import ConfigError
            raise ConfigError('Tag "%s" doesn\'t have any source code associated with it.' % name)
        project.add_tag(self)

    def delete(self):
        if path.exists(self.scores_filename):
            os.remove(self.scores_filename)
        if path.exists(self.source_filename):
            os.remove(self.source_filename)
        self.project.remove_tag(self)

    def update(self):
        self.project.remove_tag(self)
        self.source_hash = self.project.source_hash
        copyfile(self.project.source, self.source_filename)
        self.project.add_tag(self)

    @property
    def time_created(self):
        return datetime.fromtimestamp(path.getmtime(self.source_filename))
