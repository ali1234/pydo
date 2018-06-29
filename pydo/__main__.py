import argparse
import os
import importlib
import importlib.util
import pathlib

from importlib.abc import MetaPathFinder

import sys

import pydo.commands

class MyImporter(MetaPathFinder):

    def __init__(self, path):
        self._path = path

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('pydo.project'):
            parts = fullname.split('.')
            path = self._path / pathlib.Path(*parts[2:]) / 'do.py'
            spec = importlib.util.spec_from_file_location(fullname, path)
            spec.submodule_search_locations=[]
            return spec
        return None

def find_project_root():
    path = pathlib.Path('.').resolve()
    if (path / 'do.top').exists():
        return path
    for p in reversed(path.parents):
        if (p / 'do.top').exists():
            return p
    raise Exception('Not in a pydo project.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--directory', type=str, default=None, help='Change directory before doing anything.')
    parser.add_argument('command', type=str, help='Command to invoke.')

    args = parser.parse_args()

    if args.directory is not None:
        os.chdir(args.directory)

    project_root = find_project_root()
    sys.meta_path.insert(0, MyImporter(project_root))
    current_dir = pathlib.Path('.').resolve().relative_to(project_root)
    mod_name = '.'.join(['pydo.project'] + list(current_dir.parts))

    mod = importlib.import_module(mod_name)

    try:
        pydo.commands.commands[mod_name][args.command]()
    except KeyError:
        print('No such command.')

if __name__ == '__main__':
    main()