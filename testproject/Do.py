from pydo import *

import pydo.project.subdir

@command
def clean():
    print('clean', __name__)
    pydo.project.subdir.clean()