import os
import sys
from collections import defaultdict
from functools import wraps

commands = defaultdict(dict)



def log(f):
    @wraps(f)
    def _log(*args, **kwargs):
        print(f.__qualname__, f.__module__, *args, **kwargs)
        f(*args, **kwargs)
    return _log


def cd(f):
    module = sys.modules[f.__module__]
    @wraps(f)
    def _cd(*args, **kwargs):
        cwd = os.getcwd()
        os.chdir(module.__path__[0])
        f(*args, **kwargs)
        os.chdir(cwd)
    return _cd


def command(f):
    c = cd(log(f))
    commands[f.__module__][f.__name__] = c
    return c
