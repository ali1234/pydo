import os
import pathlib
import sys
from collections import defaultdict
from functools import wraps

import logging
logger = logging.getLogger(__name__)

commands = defaultdict(dict)

def cwd(f, module):
    @wraps(f)
    def _cwd(*args, **kwargs):
        old_dir = os.getcwd()
        os.chdir(pathlib.Path(module.__file__).parent)
        logger.debug('module={:s}, cwd={:s}, command={:s}'.format(module.__file__, os.getcwd(), f.__name__))
        result = f(*args, **kwargs)
        os.chdir(old_dir)
        return result
    return _cwd


def command(f):
    module = sys.modules[f.__module__]
    _command = cwd(f, module)
    commands[module.__package__][f.__name__] = _command
    return _command
