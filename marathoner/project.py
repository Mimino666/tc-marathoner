import hashlib
import os
from os import path
import shlex
import time

from six import print_, iteritems
from six.moves import configparser

from marathoner.contest.simple import Contest
from marathoner.scores import Scores
from marathoner.tag import Tag
from marathoner.utils.ossignal import get_signal_name
from marathoner.utils.proc import start_process


class ConfigError(Exception):
    pass


class Project(object):
    # dict of all available fields
    #   format: {field_name: is_required}
    FIELDS = {
        'visualizer': True,
        'solution': True,
        'source': True,
        'testcase': False,
        'maximize': True,
        'novis': False,
        'vis': False,
        'params': False,
    }

    # fields, that should point to existing files
    EXISTING_FILE_FIELDS = frozenset(['visualizer', 'source'])

    def __init__(self, root_path='.'):
        self.project_dir = path.abspath(root_path)
        self.project_name = path.basename(self.project_dir)

        # init cfg
        self.cfg_path = self.data_path('marathoner.cfg')
        if not path.exists(self.cfg_path):
            raise ConfigError('Unable to find marathoner.cfg file.')
        cfg = configparser.SafeConfigParser()
        cfg.read([self.cfg_path])

        for field_name, required in iteritems(self.FIELDS):
            value = cfg.get('marathoner', field_name)
            if not value and required:
                raise ConfigError('Field "%s" in marathoner.cfg is required.' % field_name)
            # clean field value
            clean_func_name = 'clean_%s' % field_name
            if hasattr(self, clean_func_name):
                value = getattr(self, clean_func_name)(value)
            if value and field_name in self.EXISTING_FILE_FIELDS:
                if not path.exists(value):
                    raise ConfigError('Field "%s" in marathoner.cfg is pointing to non-existent file: %s' %
                                      (field_name, value))
                if not path.isfile(value):
                    raise ConfigError('Field "%s" in marathoner.cfg is not pointing to a file: %s' %
                                      (field_name, value))
            setattr(self, field_name, value)

        self.source_ext = path.splitext(self.source)[-1]
        self.mediator = __import__('marathoner.mediator', fromlist=['mediator']).__file__
        self.mediator = path.splitext(self.mediator)[0] + '.py'
        self.scores = Scores(self, self.data_path('scores.txt'))
        self.contest = Contest(self)

        # collect available source codes in tag directory
        sources = {}
        for filename in os.listdir(self.tags_dir):
            base, ext = path.splitext(filename)
            if ext != '.score':
                sources[path.basename(base)] = filename
        # initialize available tags
        for filename in os.listdir(self.tags_dir):
            base, ext = path.splitext(filename)
            if ext == '.score':
                name = path.basename(base)
                source_filename = sources.get(name)
                if source_filename is None:
                    raise ConfigError('Tag "%s" doesn\'t have any source code associated with it.' % name)
                tag = Tag(self, name, source_filename)
                self.scores.update(tag.scores)

    def data_path(self, path_, create_dirs=False):
        '''If path is relative, return the given path inside the project dir,
        otherwise return the path unmodified.
        '''
        if not path.isabs(path_):
            path_ = path.join(self.project_dir, path_)
        if create_dirs and not path.exists(path_):
            os.makedirs(path_)
        return path_

    def hash_of_file(self, filename):
        # calculate the hash of the file
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            md5.update(f.read())
        return md5.hexdigest()

    @property
    def tags(self):
        return Tag.name_to_tag

    @property
    def tags_dir(self):
        return self.data_path('tags', create_dirs=True)

    _source_mtime = None
    _source_hash = None
    @property
    def source_hash(self):
        '''Return the hash of the current version of source code.
        Cache the hash value, between the changes of the file.
        '''
        mtime = path.getmtime(self.source)
        if mtime != self._source_mtime:
            self._source_mtime = mtime
            self._source_hash = self.hash_of_file(self.source)
        return self._source_hash

    @property
    def current_tag(self):
        '''Return the current instance of Tag, based on the current hash
        of the source code.
        '''
        return Tag.hash_to_tag.get(self.source_hash)

    def clean_solution(self, value):
        parsed_value = shlex.split(value)
        # try to run the solution to check if it works
        try:
            solution_proc = start_process(parsed_value)
        except:
            raise ConfigError('Field "solution" in marathoner.cfg is not properly configured. Try to run from command line:\n    %s' % value)

        time.sleep(0.5)
        code = solution_proc.poll()
        if code:
            raise ConfigError('Your solution program doesn\'t work. '
                              'When we run it, it ends with non-zero code: %s' % get_signal_name(code))
        elif code is not None:
            raise ConfigError('Your solution program doesn\'t work. '
                              'When we run it, it immediatelly ends.')

        solution_proc.kill()
        return parsed_value

    def clean_testcase(self, value):
        if value:
            if path.exists(value) and not path.isfile(value):
                raise ConfigError('Field "testcase" in marathoner.cfg is not pointing to a file: %s' % value)
            if path.exists(value):
                print_('WARNING: File %s already exists and will be overwritten by visualizer\'s input data.\n' % value)
        return value

    def clean_maximize(self, value):
        value = value.lower()
        if value not in ['true', 'false']:
            raise ConfigError('Value for "maximize" field in marathoner.cfg '
                              'has to be either "true" or "false".')
        return value == 'true'

    def clean_params(self, value):
        return shlex.split(value)
