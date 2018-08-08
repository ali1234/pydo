import pathlib

from pydo import *

from . import subdir

@command(consumes=[subdir.output])
def check():
    call([
        f'cat {subdir.output}',
    ])
