class BaseCommand(object):
    syntax = ''
    help = ''

    def __init__(self, project, executor):
        self.project = project
        self.executor = executor

    def is_match(self, command):
        raise NotImplementedError()

    def handle(self, command, vis_params):
        pass
