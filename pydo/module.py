import pathlib
import types
from functools import wraps

import importlib.util

def log(f):
    @wraps(f)
    def _log(self, *args, **kwargs):
        print(f.__name__, f.__module__, *args, **kwargs)
        f(self, *args, **kwargs)
    return _log


def debugmethods(cls):
    for k, v in vars(cls).items():
        if callable(v):
            setattr(cls, k, log(v))
    return cls


class ModuleMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        clsobj = super().__new__(cls, clsname, bases, clsdict)
        return debugmethods(clsobj)

class Module(types.ModuleType, metaclass=ModuleMeta):

    def some_function(self):
        pass

    @property
    def working_dir(self):
        return pathlib.Path(self.__path__[0])