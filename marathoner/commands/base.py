class CommandSyntaxError(Exception):
    pass


class BaseCommand(object):
    syntax = ''
    help = ''

    def __init__(self, project, executor):
        self.project = project
        self.executor = executor
        self.contest = project.contest

    def is_match(self, command):
        '''Given is the text that user typed into command line, return True
        if this command should execute.
        '''
        raise NotImplementedError()

    def handle(self, command):
        '''Given is the text that user typed into command line, execute the
        command.
        '''
