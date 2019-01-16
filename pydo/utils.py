import logging
import shlex
import subprocess
from textwrap import TextWrapper

from .loghelper import findlogger

@findlogger
def textwrap(logger, string_or_list, prefix='', join=' ', width=120):
    """Generates wordwrapped lines for config files."""

    wrapper = TextWrapper(
        break_long_words=False, break_on_hyphens=False,
        initial_indent=prefix, subsequent_indent=prefix,
        width=width,
    )

    if isinstance(string_or_list, str):
        result = wrapper.fill(string_or_list)
    else:
        result = wrapper.fill(join.join(string_or_list))

    logger.debug(f'textwrap output: {repr(result)}')

    return result

@findlogger
def subst(logger, template, output, substitutions):
    i = template.read_text()

    logger.debug(f'subst input: {repr(i)}')
    logger.debug(f'subst substitutions: {substitutions}')

    for k, v in substitutions.items():
        i = i.replace(k, v)

    logger.debug(f'subst output: {repr(i)}')

    if output.exists() and output.read_text() == i:
        return
    else:
        output.write_text(i)

verbosity = 1

@findlogger
def call(logger, commands, check=True, shell=False, env=None):
    for c in commands:
        logger.info(c)
        if not shell:
            c = shlex.split(c)
        subprocess.run(
            c, check=check, shell=shell, env=env,
            stdout=subprocess.DEVNULL if verbosity < 2 else None,
            stderr=subprocess.DEVNULL if verbosity < 1 else None,
        )
