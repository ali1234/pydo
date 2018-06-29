import os
import sys
from collections import defaultdict

commands = defaultdict(dict)


def command(f):
    module = sys.modules[f.__module__]
    def logger(*args, **kwargs):
        cwd = os.getcwd()
        os.chdir(module.__path__[0])
        print(f.__name__, f.__module__, *args, **kwargs)
        f(*args, **kwargs)
        os.chdir(cwd)
    commands[f.__module__][f.__name__] = logger
    return logger
