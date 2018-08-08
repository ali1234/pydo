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


def command(produces=[], consumes=[]):

    def _command(f):
        module = sys.modules[f.__module__]
        name = f'{module.__name__.partition(".")[2]}:{f.__name__}'
        @wraps(f)
        def __command():

            for c in consumes:
                if c in producers:
                    producers[c]()

            # if f has no products it must have been explicitly invoked
            # so run it unconditionally
            if len(produces) == 0:
                logger.debug(f'Running {name} because it has no products.')
                return f()

            for p in produces:
                if not p.exists:
                    logger.debug(f'Running {name} because {p} doesn\'t exist.')
                    return f()

            for p, c in itertools.product(produces, consumes):
                if p.stat().st_mtime < c.stat().st_mtime:
                    logger.debug(f'Running {name} because {p} is older than {c}.')
                    return f()

            logger.debug('{name} is up to date.')


        for product in produces:
            producers[product] = __command

        consumers[__command] = consumes

        commands[module.__package__][f.__name__] = __command
        return __command

    return _command

