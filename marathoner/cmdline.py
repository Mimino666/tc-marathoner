import os
import re
import shutil
import sys

from six import print_, itervalues
from six.moves import input

import marathoner
from marathoner.commands import collect_commands
from marathoner.commands.base import CommandSyntaxError
from marathoner.executor import Executor
from marathoner.project import Project, ConfigError


class UsageError(Exception):
    pass


def new_marathoner_command(args):
    if len(args) != 1:
        raise UsageError('Exactly one argument is required.')
    project_name = args[0]
    if not re.match(r'^[_a-zA-Z]\w*$', project_name):
        print_('Error: Project name must begin with a letter and '
               'contain only letters, numbers and underscores.')
        sys.exit(1)
    elif os.path.exists(project_name):
        print_('Error: directory "%s" already exists' % project_name)
        sys.exit(1)

    templates_path = os.path.join(marathoner.__path__[0], 'templates', 'project')
    shutil.copytree(templates_path, project_name)


def run_marathoner_command(args):
    project = Project(args[0] if args else '.')
    executor = Executor(project)
    commands = [cmd(project, executor) for cmd in itervalues(collect_commands())]

    print_('Welcome to Marathoner %s!' % marathoner.__version__)
    print_('You are now working on project "%s".' % project.project_name)
    print_('Type "help" to see the list of available commands.')

    try:  # readline module is only available on unix systems
        import readline
    except ImportError:
        pass
    while True:
        try:
            user_input = input('>>> ').strip()
        except EOFError:
            return
        if not user_input:
            continue
        for cmd in commands:
            if cmd.is_match(user_input):
                try:
                    cmd.handle(user_input)
                except CommandSyntaxError:
                    print_('Help:   ', cmd.help)
                    print_('Syntax: ', cmd.syntax)
                break
        else:
            print_('Unrecognized command. Type "help" to see the list of available commands.')


available_commands = {
    'new': (new_marathoner_command, '<project_name>', 'Create a new marathoner project.'),
    'run': (run_marathoner_command, '[path_to_project]', 'Run existing marathoner project.')
}


def print_usage(cmd_name, help):
    _, cmd_syntax, cmd_help = available_commands[cmd_name]
    cmd = '%s %s' % (cmd_name, cmd_syntax)
    if help:
        print_('  marathoner %-25s %s' % (cmd, cmd_help))
    else:
        print_('  marathoner %s' % cmd)


def print_help():
    print_('Marathoner %s\n' % marathoner.__version__)
    print_('Available commands:')
    for cmd_name in available_commands:
        print_usage(cmd_name, help=True)


def execute(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) <= 1:
        print_help()
        sys.exit(0)

    cmd_name, args = argv[1], argv[2:]
    if cmd_name not in available_commands:
        print_('Unknown command: %s\n' % cmd_name)
        print_('Type "marathoner" to see the available commands.')
        sys.exit(2)
    cmd_func = available_commands[cmd_name][0]

    try:
        cmd_func(args)
    except UsageError as e:
        print_('%s\nUsage:' % e)
        print_usage(cmd_name, help=False)
        sys.exit(2)
    except ConfigError as e:
        print_(e)
        sys.exit(2)

if __name__ == '__main__':
    execute()
