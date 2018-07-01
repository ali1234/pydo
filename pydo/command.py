import os
import sys
from functools import wraps


def command(f):
    if f.__name__ in ['check', 'build']:
        raise NameError
    module = sys.modules[f.__module__]
    @wraps(f)
    def _command(*args, **kwargs):
        cwd = os.getcwd()
        os.chdir(module.working_dir)
        result = f(*args, **kwargs)
        os.chdir(cwd)
        return result
    module.__commands__[f.__name__] = _command
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

