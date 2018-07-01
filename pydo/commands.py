import os
import sys
from collections import defaultdict
from functools import wraps

user_commands = defaultdict(dict)

builtin_commands = {}

def command(f):
    if f.__name__ in builtin_commands:
        raise NameError
    module = sys.modules[f.__module__]
    @wraps(f)
    def _command(*args, **kwargs):
        cwd = os.getcwd()
        os.chdir(module.working_dir)
        result = f(*args, **kwargs)
        os.chdir(cwd)
        return result
    user_commands[module.__package__][f.__name__] = _command
    return _command


def default_command(f):
    @wraps(f)
    def _command(self, *args, **kwargs):
        cwd = os.getcwd()
        os.chdir(self.working_dir)
        result = f(self, *args, **kwargs)
        os.chdir(cwd)
        return result
    return _command


def builtin_command(f):
    builtin_commands[f.__name__] = f
    return f


@builtin_command
def build(m):
    for d in m.recursive_deps:
        if d._check():
            print('Building', d.friendly_name)
            d._build()
    if m._check():
        print('Building', m.friendly_name)
        m._build()


@builtin_command
def check(m):
    result = False
    for d in m.recursive_deps:
        if d._check():
            print(d.friendly_name)
            result = True
    if m._check():
        print(m.friendly_name)
        result = True
    return result


@builtin_command
def deps(m):
    result = False
    for d in m.recursive_deps:
        print(d.friendly_name)