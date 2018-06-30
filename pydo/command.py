import os
import sys
from functools import wraps


def command(f):
    module = sys.modules[f.__module__]
    @wraps(f)
    def _command(*args, **kwargs):
        cwd = os.getcwd()
        os.chdir(module.__working_dir__)
        print(f.__qualname__, f.__module__, *args, **kwargs)
        f(*args, **kwargs)
        os.chdir(cwd)
    module.__commands__[f.__name__] = _command
    return _command


def default_command(f):
    @wraps(f)
    def _command(self, *args, **kwargs):
        cwd = os.getcwd()
        os.chdir(self.__working_dir__)
        print(f.__name__, '(default)', self.__name__, *args, **kwargs)
        f(self, *args, **kwargs)
        os.chdir(cwd)
    _command.__default_command = True
    return _command


def gather_default_commands(cls):
    for k, v in vars(cls).items():
        if hasattr(v, '__default_command'):
            cls.__default_commands__[k] = v
    return cls