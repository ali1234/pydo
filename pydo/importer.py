import importlib
import importlib.abc
import importlib.util
import pathlib

from .module import ProjectModule


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

    def exec_module(self, module):
        code = self.get_code(module.__name__)
        exec(code, module.__dict__)
        print('LOADED', module, module.__name__, module.__package__)


def this_module() -> ProjectModule:
    filename = inspect.currentframe().f_back.f_code.co_filename

    for m in sys.modules.values():
        if getattr(m, '__file__', None) == filename:
            if isinstance(m, ProjectModule):
                return m

    raise TypeError('this_module() can only be called in Dofiles.')