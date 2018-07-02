import importlib
import inspect
import pathlib
import types

from descriptors import Descriptor, Bool, List

from .commands import module_command


def validated(cls):
    for k, v in vars(cls).items():
        if isinstance(v, Descriptor):
            v.name = k
    return cls


@validated
class ProjectModule(types.ModuleType):
    enabled = Bool()
    dependencies = List()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enabled = True

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
            if m.enabled:
                yield m

    @property
    def friendly_name(self):
        return '/'.join(self.__package__.split('.')[1:])

    def walk(self, seen):
        if id(self) in seen:
            return
        seen.add(id(self))
        for d in self.auto_deps:
            yield from d.walk(seen)
        yield self

    @property
    def auto_deps(self):
        try:
            return self.dependencies
        except AttributeError:
            return self.enabled_submodules

    @property
    def recursive_deps(self):
        seen = set()
        for m in self.auto_deps:
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


def this_module() -> ProjectModule:
    return inspect.getmodule(inspect.currentframe().f_back)
