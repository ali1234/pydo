import importlib
import pathlib

from .commands import module_command


class ProjectModule(object):

    def __init__(self):
        self.__enabled__ = True

    @property
    def working_dir(self):
        return pathlib.Path(self.__path__[0])

    @property
    def submodules(self):
        for p in self.working_dir.iterdir():
            if p.is_dir() and (p / 'Dofile').exists():
                yield importlib.import_module('.'.join([self.__package__, p.name]))

    @property
    def enabled_submodules(self):
        for m in self.submodules:
            if m.__enabled__:
                yield m

    @property
    def friendly_name(self):
        return '/'.join(self.__package__.split('.')[1:])

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
            return self.enabled_submodules

    @property
    def recursive_deps(self):
        seen = set()
        for m in self.dependencies:
            yield from m.walk(seen)

    @module_command
    def _check(self):
        try:
            return self.check()
        except AttributeError:
            return True

    @module_command
    def _build(self):
        try:
            self.build()
        except AttributeError:
            pass
