from ConfigParser import SafeConfigParser
from os import path


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
    EXISTING_FILE_FIELDS = frozenset(['visualizer', 'solution', 'source'])

    def __init__(self, root_path='.'):
        self.cfg_path = path.abspath(path.join(root_path, 'marathoner.cfg'))
        if not path.exists(self.cfg_path):
            raise ConfigError('Unable to find marathoner.cfg file.')
        # init cfg
        cfg = SafeConfigParser()
        cfg.read([self.cfg_path])

        for field_name, required in self.FIELDS.iteritems():
            value = cfg.get('marathoner', field_name)
            # clean field value
            clean_func_name = 'clean_%s' % field_name
            if hasattr(self, clean_func_name):
                value = getattr(self, clean_func_name)(value)
            if value is None and required:
                raise ConfigError('Field "%s" in marathoner.cfg is required.' % field_name)
            if value and field_name in self.EXISTING_FILE_FIELDS:
                if not path.exists(value):
                    raise ConfigError('Field "%s" in marathoner.cfg is pointing to non-existent file: %s' %
                                      (field_name, value))
                if not path.isfile(value):
                    raise ConfigError('Field "%s" in marathoner.cfg is not pointing to a file: %s' %
                                      (field_name, value))
            setattr(self, field_name, value)

    def clean_testcase(self, value):
        if value:
            if path.exists(value) and not path.isfile(value):
                raise ConfigError('Field "testcase" in marathoner.cfg is not pointing to a file: %s' % value)
            if path.exists(value):
                print 'WARNING: File %s already exists and will be overwritten by testcase input.\n' % value
        return value

    def clean_maximize(self, value):
        value = value.lower()
        if value not in ['true', 'false']:
            raise ConfigError('Value for "maximize" field in marathoner.cfg '
                              'has to be either "true" or "false".')
        return value == 'true'

    def clean_params(self, value):
        return value.split()
