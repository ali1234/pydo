import importlib
import pathlib

from descriptors import Descriptor, Bool, List, Callable

from .helpers import check_timestamps
from .commands import cwd


def validated(cls):
    for k, v in vars(cls).items():
        if isinstance(v, Descriptor):
            v.name = k
    return cls


@validated
class ProjectModule(object):
    enabled = Bool()
    dependencies = List()
    sources = List()
    targets = List()
    build = Callable()
    check = Callable()

    def __init__(self, *args, **kwargs):
        self.enabled = True
        self.build = lambda: None

        def _check(verbose=True):
            if hasattr(self, 'targets'):
                return check_timestamps(list(self.auto_sources), self.targets, verbose=verbose)
            else:
                return True
        self.check = cwd(_check, self)

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

    @property
    def auto_sources(self):
        try:
            yield from self.sources
        except AttributeError:
            for m in self.auto_deps:
                if hasattr(m, 'targets'):
                    yield from (str(m.working_dir / t) for t in m.targets)

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
            yield from self.dependencies
        except AttributeError:
            yield from self.enabled_submodules

    @property
    def recursive_deps(self):
        seen = set()
        for m in self.auto_deps:
            yield from m.walk(seen)

