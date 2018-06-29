import argparse
import os
import importlib
import importlib.util
import pathlib

from importlib.abc import MetaPathFinder

import sys


class MyImporter(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('pydo.project'):
            parts = fullname.split('.')
            path = pathlib.Path(*parts[2:]) / 'do.py'
            spec = importlib.util.spec_from_file_location(fullname, path)
            spec.submodule_search_locations=[path]
            return spec
        return None

def path_finder(a):
    print(a)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--directory', type=str, default=None, help='Change directory before doing anything.')

    args = parser.parse_args()

    if args.directory is not None:
        os.chdir(args.directory)

    sys.meta_path.insert(0, MyImporter())

    import pydo.project
    pydo.project.main()


if __name__ == '__main__':
    main()