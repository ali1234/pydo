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


def build_command(m):
    for d in m.recursive_deps:
        if d._check():
            d._build()
    if m._check():
        m._build()


def check_command(m):
    result = False
    for d in m.recursive_deps:
        if d._check():
            print(d.friendly_name)
            result = True
    if m._check():
        print(m.friendly_name)
        result = True
    return result


def deps_command(m):
    result = False
    for d in m.recursive_deps:
        print(d.friendly_name)



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
        sys.meta_path.insert(0, pydo.importer.ProjectFinder(project_root))
        current_dir = pathlib.Path('.').resolve().relative_to(project_root)
        mod_name = '.'.join(['pydo.project'] + list(current_dir.parts))
        mod = importlib.import_module(mod_name)
        if args.command == 'build':
            build_command(mod)
        elif args.command == 'check':
            check_command(mod)
        elif args.command == 'deps':
            deps_command(mod)
        else:
            try:
                mod.__commands__[args.command](*args.args)
            except KeyError:
                print('No such command.')


if __name__ == '__main__':
    main()