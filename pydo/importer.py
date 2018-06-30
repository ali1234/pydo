import importlib
import importlib.abc
import importlib.util
import pathlib
import types

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


class ProjectModule(types.ModuleType):

    __default_commands__ = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__commands__ = {}

    @property
    def __working_dir__(self):
        return pathlib.Path(self.__path__[0])

    @property
    def __submodules__(self):
        for p in self.__working_dir__.iterdir():
            if p.is_dir() and (p / 'Dofile').exists():
                yield importlib.import_module('.'.join([self.__package__, p.name]))
