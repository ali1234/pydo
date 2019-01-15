import argparse
import os
import importlib
import pathlib
import sys
import logging

from . import loghelper
from . import commands
from . import utils

class ProjectNotFound(Exception):
    pass

class CommandNotFound(Exception):
    pass

class SubmoduleNotFound(Exception):
    pass

class MalformedCommand(Exception):
    pass



def find_project_root():
    path = pathlib.Path('.').resolve()
    if (path / '.pydo').is_dir():
        return path
    for p in reversed(path.parents):
        if (p / '.pydo').is_dir():
            return p
    raise ProjectNotFound


def parse_command(command, project_root):
    current_dir = pathlib.Path('.').resolve().relative_to(project_root.parent)

    if len(command) == 1:
        mod_name = '.'.join(list(current_dir.parts))
        command = command[0]
    elif len(command) == 2:
        if len(command[0]) > 0:
            mod_name = '.'.join([project_root.name, command[0]])
        else:
            mod_name = project_root.name
        command = command[1]
    else:
        raise MalformedCommand(command)
    return (mod_name, command)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--debug', action='store_true', help='Print internal debugging messages.')
    parser.add_argument('-C', '--directory', type=str, default=None, help='Change directory before doing anything.')
    parser.add_argument('-c', '--colour', action='store_true', help='Force colour output.')
    parser.add_argument('-s', '--subprocess-verbosity', type=int, default=1, help='How much output to show from called subprocesses.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--init', action='store_true', help='Initialize project.')
    group.add_argument('-l', '--commands', action='store_true', help='List available commands.')
    group.add_argument('-H', '--helpcmd', type=str, metavar='COMMAND', nargs='?', default=None, help='Show help for command.')
    group.add_argument('command', type=str, metavar='COMMAND', nargs='?', default=None, help='Command to invoke.')


    args = parser.parse_args()

    loghelper.config(args.debug, args.colour or sys.stdout.isatty())

    logger = logging.getLogger('core')

    utils.verbosity = args.subprocess_verbosity

    if args.directory is not None:
        os.chdir(args.directory)

    if args.init:
        pathlib.Path('.pydo').mkdir()
        exit(0)

    try:
        commands.project_root = find_project_root()
        sys.path.insert(0, str(commands.project_root.parent))
        importlib.import_module(commands.project_root.name)

        if args.commands:
            print('Command list:')
            for module, d in commands.commands.items():
                for c, f in d.items():
                    print(f'{module.partition(".")[2]}:{f.__name__}')
        else:
            raw_command = (args.command or args.helpcmd).split(':')
            mod_name, command = parse_command(raw_command, commands.project_root)
            try:
                mod = importlib.import_module(mod_name)
            except ModuleNotFoundError as e:
                if e.name == mod_name:
                    raise SubmoduleNotFound(mod_name.partition('.')[2])
                else:
                    raise e
            try:
                f = commands.commands[mod.__name__][command]
            except KeyError:
                raise CommandNotFound(f'"{mod_name.partition(".")[2]}"' or 'the root of this project', command)
            if args.command:
                f()
            elif args.helpcmd:
                help(f)

    except ProjectNotFound as e:
        logger.error('Not in a pydo project.')
        exit(-1)

    except CommandNotFound as e:
        logger.error(f'"{e.args[1]}" is not a command in {e.args[0]}. See "pydo -l" for a list of available commands.')
        exit(-1)

    except SubmoduleNotFound as e:
        logger.error(f'"{e.args[0]}" is not a submodule in this project. See "pydo -l" for a list of available commands.')
        exit(-1)

    except MalformedCommand as e:
        logger.error(f'Malformed command: "{args.command or args.helpcmd}".')
        exit(-1)

if __name__ == '__main__':
    main()
