import importlib
import importlib.abc
import importlib.util
import pathlib
import types
from functools import wraps

from pydo.command import command, default_command, gather_default_commands


class ProjectFinder(importlib.abc.MetaPathFinder):

    def __init__(self, path):
        self._path = path
        super().__init__()

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('pydo.project'):
            return importlib.util.spec_from_loader(fullname, ProjectLoader(fullname, self._path))
        return None


class ProjectLoader(importlib.abc.FileLoader):

    def create_module(self, spec):
        return ProjectModule(spec.name)

    def is_package(self, fullname):
        return True

    def get_filename(self, fullname):
        parts = fullname.split('.')
        origin = self.path / pathlib.Path(*parts[2:]) / 'Dofile'
        if origin.exists():
            return str(origin)
        else:
            raise ImportError

    def get_source(self, fullname):
        try:
            return pathlib.Path(self.get_filename(fullname)).read_text()
        except Exception:
            raise ImportError


@gather_default_commands
class ProjectModule(object):

    __default_commands__ = {}

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__commands__ = {}
        self.__self__ = self
        self.command = command
        self.__defaults__ = ProjectModule

    @property
    def __working_dir__(self):
        return pathlib.Path(self.__path__[0])

    @property
    def __submodules__(self):
        for p in self.__working_dir__.iterdir():
            if p.is_dir() and (p / 'Dofile').exists():
                yield importlib.import_module('.'.join([self.__package__, p.name]))

    def walk(self, seen):
        if id(self) in seen:
            return
        seen.add(id(self))
        for d in self.__auto_deps__:
            yield from d.walk(seen)
        yield self

    @property
    def __auto_deps__(self):
        try:
            return self.__dependencies__
        except AttributeError:
            return self.__submodules__

    @property
    def __recursive_deps__(self):
        seen = set()
        for m in self.__auto_deps__:
            yield from m.walk(seen)

    @default_command
    def check(self):
        return True

    @default_command
    def build(self):
        pass

    @default_command
    def default(self):
        for m in self.__recursive_deps__:
            if m.check():
                m.build()
        if self.check():
            self.build()