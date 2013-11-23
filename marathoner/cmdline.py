import os
import re
import shutil
import sys

import marathoner
from marathoner.commands import collect_commands
from marathoner.executor import Executor
from marathoner.project import Project


class UsageError(Exception):
    pass


def new_marathoner(args):
    if len(args) != 1:
        raise UsageError('Exactly one argument is required.')
    project_name = args[0]
    if not re.search(r'^[_a-zA-Z]\w*$', project_name):
        print ('Error: Project names must begin with a letter and '
               'contain only letters, numbers and underscores.')
        sys.exit(1)
    elif os.path.exists(project_name):
        print 'Error: directory "%s" already exists' % project_name
        sys.exit(1)

    templates_path = os.path.join(marathoner.__path__[0], 'templates', 'project')
    shutil.copytree(templates_path, project_name)


def run_marathoner(args):
    project = Project(args[0] if args else '.')
    executor = Executor(project)
    commands = [cmd(project, executor) for cmd in collect_commands().itervalues()]
    while True:
        user_input = raw_input('>>> ').strip()
        if not user_input:
            continue
        for cmd in commands:
            if cmd.is_match(user_input):
                cmd.handle(user_input)
                break
        else:
            print 'Unrecognized command. Type "help" to see the list of available commands.'


available_commands = {
    'new': (new_marathoner, '<project_name>', 'Create a new marathoner project.'),
    'run': (run_marathoner, '[path_to_project]', 'Run marathoner from the current directory.')
}


def print_usage(cmd_name, help):
    _, cmd_syntax, cmd_help = available_commands[cmd_name]
    cmd = '%s %s' % (cmd_name, cmd_syntax)
    if help:
        print '  %-25s %s' % (cmd, cmd_help)
    else:
        print '  %s' % cmd


def print_help():
    print 'Marathoner %s\n' % marathoner.__version__

    print 'Usage:'
    print '  marathoner <command> [args]'
    print
    print 'Available commands:'
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
        print 'Unknown command: %s\n' % cmd_name
        print 'Use "marathoner" to see available commands'
        sys.exit(2)
    cmd_func = available_commands[cmd_name][0]

    try:
        cmd_func(args)
    except UsageError as e:
        print e
        print '\nUsage:'
        print_usage(cmd_name, help=False)
        sys.exit(2)
    except Exception as e:
        print e
        sys.exit(2)


if __name__ == '__main__':
    execute()
