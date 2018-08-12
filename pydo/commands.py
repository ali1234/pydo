import itertools
import os
import pathlib
import sys
from collections import defaultdict
from functools import wraps

import logging
logger = logging.getLogger(__name__)

commands = defaultdict(dict)
producers = {}
consumers = {}

def walk_producers(f, result, seen):
    if f in seen:
        return
    seen.add(f)
    for c in consumers[f]:
        if c in producers:
            walk_producers(producers[c], result, seen)
    result.append(f)

def command(produces=[], consumes=[], always=False):

    def _command(f):
        module = sys.modules[f.__module__]
        name = f'{module.__name__.partition(".")[2]}:{f.__name__}'

        logger.debug(f'Registering command {name} : {consumes} => {produces}.')

        @wraps(f)
        def _run_cmd_if_necessary():

            if always:
                logger.debug(f'Running {name} because always is True.')
                return f()

            # if f has no products it must have been explicitly invoked
            # so run it unconditionally
            if len(produces) == 0:
                logger.debug(f'Running {name} because it has no products.')
                return f()

            for p in produces:
                if not p.exists():
                    logger.debug(f'Running {name} because {p} doesn\'t exist.')
                    return f()

            for p, c in itertools.product(produces, consumes):
                if p.stat().st_mtime < c.stat().st_mtime:
                    logger.debug(f'Running {name} because {p} is older than {c}.')
                    return f()

            logger.debug(f'{name} is up to date.')

        for product in produces:
            producers[product] = _run_cmd_if_necessary

        consumers[_run_cmd_if_necessary] = consumes

        @wraps(_run_cmd_if_necessary)
        def _consider_cmd_and_deps():
            logger.debug(f'Considering {name}...')

            deps = []
            walk_producers(_run_cmd_if_necessary, deps, set())
            for f in deps:
                f()

        if f.__name__[0] != '_':
            commands[module.__package__][f.__name__] = _consider_cmd_and_deps
        return _consider_cmd_and_deps

    return _command

