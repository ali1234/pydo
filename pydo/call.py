import shlex
import subprocess

import logging

logger = logging.getLogger(__name__)


def call(commands, check=True, shell=False, env=None):
    for c in commands:
        logger.info(c)
        if not shell:
            c = shlex.split(c)
        subprocess.run(c, check=check, shell=shell, env=env)
