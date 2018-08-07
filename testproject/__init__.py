import os

from pydo import *

@command
def usercommand():
    '''
    Help for usercommand.
    '''
    subdir.subcommand()

from . import subdir
