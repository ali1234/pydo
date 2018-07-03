import importlib
import pathlib

from descriptors import Descriptor, Bool, List, Callable


def validated(cls):
    for k, v in vars(cls).items():
        if isinstance(v, Descriptor):
            v.name = k
    return cls


@validated
class ProjectModule(object):
    enabled = Bool()
    dependencies = List()
    build = Callable()
    check = Callable()

    def __init__(self, *args, **kwargs):
        self.enabled = True
        self.build = lambda: None
        self.check = lambda: True

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

