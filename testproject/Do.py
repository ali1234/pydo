from pydo import *

import pydo.project.subdir

@command
def clean(*args):
    pydo.project.subdir.clean(*args)