from sh import ls, pwd

from pydo import *

import pydo.project.subdir

@command
def clean(*args):
    pydo.project.subdir.clean(*args)
    print(ls('-l', 'subdir'))

@command
def build(*args):
    pydo.project.subdir.build(*args)
    print(ls('-l', 'subdir'))

@command
def all():
    build()
