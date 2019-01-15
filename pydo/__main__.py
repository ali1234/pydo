import argparse
import os
import importlib
import pathlib
import sys
import logging

from . import commands


class ProjectNotFound(Exception):
    pass

class CommandNotFound(Exception):
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--init', action='store_true', help='Initialize project.')
    group.add_argument('-l', '--commands', action='store_true', help='List available commands.')
    group.add_argument('-H', '--helpcmd', type=str, metavar='COMMAND', nargs='?', default=None, help='Show help for command.')
    group.add_argument('command', type=str, metavar='COMMAND', nargs='?', default=None, help='Command to invoke.')


    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

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
            command = (args.command or args.helpcmd).split(':')
            mod_name, command = parse_command(command, commands.project_root)
            mod = importlib.import_module(mod_name)
            try:
                if args.command:
                    commands.commands[mod.__name__][command]()
                elif args.helpcmd:
                    help(commands.commands[mod.__name__][command])
            except KeyError:
                raise CommandNotFound(mod.__name__, command)

    except ProjectNotFound as e:
        logger.fatal('Not in a pydo project.')
        exit(-1)

    except CommandNotFound as e:
        logger.fatal(f'"{args.command or args.helpcmd}" is not a command. See "pydo -l" for a list of available commands.')
        exit(-1)

    except MalformedCommand as e:
        logger.fatal(f'Malformed command: "{args.command or args.helpcmd}".')
        exit(-1)

if __name__ == '__main__':
    main()
