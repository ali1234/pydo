import argparse
import os
import importlib
import importlib.util
import pathlib

from importlib.abc import *

import sys

import pydo.commands
import pydo.module


class ProjectImporter(MetaPathFinder):

    def __init__(self, path):
        self._path = path
        super().__init__()

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('pydo.project'):
            spec = importlib.util.spec_from_loader(fullname, ProjectLoader(fullname, self._path))
            return spec
        return None

class ProjectLoader(FileLoader):

    def create_module(self, spec):
        return pydo.module.Module(spec.name)

    def is_package(self, fullname):
        return True

    def get_filename(self, fullname):
        parts = fullname.split('.')
        origin = self.path / pathlib.Path(*parts[2:]) / 'Do.py'
        if origin.exists():
            return str(origin)
        else:
            raise ImportError

    def get_source(self, fullname):
        try:
            return pathlib.Path(self.get_filename(fullname)).read_text()
        except Exception:
            raise ImportError


def find_project_root():
    path = pathlib.Path('.').resolve()
    if (path / 'Do.top').exists():
        return path
    for p in reversed(path.parents):
        if (p / 'Do.top').exists():
            return p
    raise FileNotFoundError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--directory', type=str, default=None, help='Change directory before doing anything.')
    parser.add_argument('command', type=str, nargs='?', default='default', help='Command to invoke.')
    parser.add_argument('args', nargs='*')

    args = parser.parse_args()

    if args.directory is not None:
        os.chdir(args.directory)

    try:
        project_root = find_project_root()
    except FileNotFoundError:
        print('Not in a pydo project.')
        exit(-1)
    else:
        sys.meta_path.insert(0, ProjectImporter(project_root))

        import pydo.project
        pydo.project.some_function()
        print(dir(pydo.project))
        print(pydo.project.working_dir)

        current_dir = pathlib.Path('.').resolve().relative_to(project_root)
        mod_name = '.'.join(['pydo.project'] + list(current_dir.parts))
        importlib.import_module(mod_name)
        try:
            pydo.commands.commands[mod_name][args.command](*args.args)
        except KeyError:
            print('No such command.')


if __name__ == '__main__':
    main()