import os
from os import path

from six import print_, iteritems
from six.moves import configparser

from marathoner.contest.simple import Contest
from marathoner.scores import Scores


class ConfigError(Exception):
    pass


class Project(object):
    # dict of all available fields
    #   format: {field_name: is_required}
    FIELDS = {
        'visualizer': True,
        'solution': True,
        'source': False,
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

        self.mediator = __import__('marathoner.mediator', fromlist=['mediator']).__file__
        self.mediator = path.splitext(self.mediator)[0] + '.py'
        self.scores = Scores(self, self.data_path('scores.txt'))
        self.contest = Contest(self)

    def data_path(self, path_, create_dirs=False):
        '''If path is relative, return the given path inside the project dir,
        otherwise return the path unmodified.
        '''
        if not path.isabs(path_):
            path_ = path.join(self.project_dir, path_)
        if create_dirs and not path.exists(path_):
            os.makedirs(path_)
        return path_

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
        return value.split()
