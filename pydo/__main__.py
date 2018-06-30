import argparse
import os
import importlib
import pathlib
import sys

import pydo.importer


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
        sys.meta_path.insert(0, pydo.importer.ProjectFinder(project_root))
        current_dir = pathlib.Path('.').resolve().relative_to(project_root)
        mod_name = '.'.join(['pydo.project'] + list(current_dir.parts))
        mod = importlib.import_module(mod_name)
        try:
            mod.__commands__[args.command](*args.args)
        except KeyError:
            try:
                mod.__default_commands__[args.command](mod, *args.args)
            except KeyError:
                print('No such command.')


if __name__ == '__main__':
    main()