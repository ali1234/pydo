import os
import sys
from collections import defaultdict
from functools import wraps

user_commands = defaultdict(dict)

builtin_commands = {}


class SyntaxCheckerIgnore(object):
    pass


def command(f):
    module = sys.modules[f.__module__]

    @wraps(f)
    def _command(*args, **kwargs):
        cwd = os.getcwd()
        os.chdir(module.working_dir)
        result = f(*args, **kwargs)
        os.chdir(cwd)
        return result

    if f.__name__ in builtin_commands:
        setattr(module, f.__name__, _command)
        return SyntaxCheckerIgnore
    else:
        user_commands[module.__package__][f.__name__] = _command
        return _command


def builtin_command(f):
    builtin_commands[f.__name__] = f
    return f


@builtin_command
def build(m):
    for d in m.recursive_deps:
        if d.check():
            print('Building', d.friendly_name)
            d.build()
    if m.check():
        print('Building', m.friendly_name)
        m.build()


@builtin_command
def check(m):
    result = False
    for d in m.recursive_deps:
        if d._check():
            print(d.friendly_name)
            result = True
    if m.check():
        print(m.friendly_name)
        result = True
    return result


@builtin_command
def deps(m):
    result = False
    for d in m.recursive_deps:
        print(d.friendly_name)
