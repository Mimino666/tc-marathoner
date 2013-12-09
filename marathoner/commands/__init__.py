import inspect
from pkgutil import iter_modules

from six import itervalues


def iter_submodules(module_path):
    '''Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.
    '''
    mods = []
    mod = __import__(module_path, {}, {}, [''])
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = module_path + '.' + subpath
            if ispkg:
                mods += iter_submodules(fullpath)
            else:
                submod = __import__(fullpath, {}, {}, [''])
                mods.append(submod)
    return mods


def iter_subclasses(module_path, base_class, include_base=False):
    '''Iterate through submodules of the `module_path` and return all the
    classes that are subclasses of the `base_class`.

    If `include_base` is False, `base_class` is not returned.
    '''
    for module in iter_submodules(module_path):
        for obj in itervalues(vars(module)):
            if (inspect.isclass(obj) and
                    issubclass(obj, base_class) and
                    obj.__module__ == module.__name__ and
                    (include_base or obj is not base_class)):
                yield obj


def collect_commands():
    '''Return the dictionary (command_name -> command_class) of all the
    available commands.
    '''
    from .base import BaseCommand
    commands = {}
    for cmd in iter_subclasses('marathoner.commands', BaseCommand):
        cmd_name = cmd.__module__.split('.')[-1]
        commands[cmd_name] = cmd
    return commands
