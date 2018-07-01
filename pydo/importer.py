import importlib
import importlib.abc
import importlib.util
import pathlib

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
        self.__defaults__ = ProjectModule
        self.command = command

    @property
    def working_dir(self):
        return pathlib.Path(self.__path__[0])

    @property
    def submodules(self):
        for p in self.working_dir.iterdir():
            if p.is_dir() and (p / 'Dofile').exists():
                yield importlib.import_module('.'.join([self.__package__, p.name]))

    def walk(self, seen):
        if id(self) in seen:
            return
        seen.add(id(self))
        for d in self.dependencies:
            yield from d.walk(seen)
        yield self

    @property
    def dependencies(self):
        try:
            return self.__dependencies__
        except AttributeError:
            return self.submodules

    @property
    def recursive_deps(self):
        seen = set()
        for m in self.dependencies:
            yield from m.walk(seen)

    @default_command
    def check(self):
        return True

    @default_command
    def build(self):
        pass

    @default_command
    def default(self):
        for m in self.recursive_deps:
            if m.check():
                m.build()
        if self.check():
            self.build()
