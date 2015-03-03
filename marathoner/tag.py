from datetime import datetime
import os
from os import path
from shutil import copyfile

from marathoner.scores import Score, Scores


class Tag(object):
    # static variables
    name_to_tag = {}  # map tag name to tag instance
    hash_to_tag = {}  # map source hash to tag instance

    def __init__(self, project, name, source_filename=None):
        self.project = project
        self.name = name
        self.scores_filename = path.join(project.tags_dir, name+'.score')
        self.scores = Scores(project, self.scores_filename)
        if source_filename is None:
            self.source_filename = path.join(project.tags_dir, name+project.source_ext)
            copyfile(self.project.source, self.source_filename)
        else:
            self.source_filename = path.join(project.tags_dir, source_filename)
        self.source_hash = project.hash_of_file(self.source_filename)
        Tag.add_tag(self)

    def __str__(self):
        return self.name

    def delete(self):
        if path.exists(self.scores_filename):
            os.remove(self.scores_filename)
        if path.exists(self.source_filename):
            os.remove(self.source_filename)
        Tag.remove_tag(self)

    def update(self):
        Tag.remove_tag(self)
        self.source_hash = self.project.source_hash
        copyfile(self.project.source, self.source_filename)
        Tag.add_tag(self)

    def get_avg_relative_score(self):
        if not len(self.scores):
            return 0.0

        score_sum = 0.0
        for seed in self.scores.seeds:
            score_sum += Score.relative_score(
                self.project.maximize,
                self.scores[seed],
                self.project.scores[seed])
        return score_sum / len(self.scores)

    @property
    def time_created(self):
        return datetime.fromtimestamp(path.getmtime(self.source_filename))

    @classmethod
    def add_tag(cls, tag):
        if tag.source_hash in cls.hash_to_tag:
            raise RuntimeError('Sources of tags "%s" and "%s" are the same.' %
                               (tag.name, cls.hash_to_tag[tag.source_hash].name))
        cls.name_to_tag[tag.name] = tag
        cls.hash_to_tag[tag.source_hash] = tag

    @classmethod
    def remove_tag(cls, tag):
        del cls.name_to_tag[tag.name]
        del cls.hash_to_tag[tag.source_hash]
