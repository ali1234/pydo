import argparse
import os
import importlib
import pathlib
import sys

from . import importer
from . import commands


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
    parser.add_argument('command', type=str, nargs='?', default='build', help='Command to invoke.')
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
        sys.meta_path.insert(0, importer.ProjectFinder(project_root))
        current_dir = pathlib.Path('.').resolve().relative_to(project_root)
        mod_name = '.'.join(['pydo.project'] + list(current_dir.parts))
        mod = importlib.import_module(mod_name)
        try:
            commands.builtin_commands[args.command](mod)
        except KeyError:
            try:
                commands.user_commands[mod.__package__][args.command](*args.args)
            except KeyError:
                print('No such command.')


if __name__ == '__main__':
    main()
