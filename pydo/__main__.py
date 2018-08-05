import argparse
import os
import importlib
import pathlib
import sys
import logging

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
    parser.add_argument('-D', '--debug', action='store_true', help='Print internal debugging messages.')
    parser.add_argument('-C', '--directory', type=str, default=None, help='Change directory before doing anything.')
    parser.add_argument('command', type=str, nargs='?', default=None, help='Command to invoke.')
    parser.add_argument('args', nargs='*')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.directory is not None:
        os.chdir(args.directory)

    try:
        project_root = find_project_root()
    except FileNotFoundError:
        print('Not in a pydo project.')
        exit(-1)
    else:
        sys.path.insert(0, str(project_root.parent))
        current_dir = pathlib.Path('.').resolve().relative_to(project_root.parent)
        mod_name = '.'.join(list(current_dir.parts))
        mod = importlib.import_module(mod_name)

        try:
            commands.commands[mod.__package__][args.command](*args.args)
        except KeyError:
            print('No such command.')


if __name__ == '__main__':
    main()
