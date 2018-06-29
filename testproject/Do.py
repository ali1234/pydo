from sh import ls, pwd

from pydo import *

import pydo.project.subdir

@command
def clean(*args):
    pydo.project.subdir.clean(*args)
    print(ls('-l', 'subdir'))

@command
def build(*args):
    print(pwd())
    print(ls('-l', 'subdir'))
    pydo.project.subdir.build(*args)

@command
def default():
    build()
