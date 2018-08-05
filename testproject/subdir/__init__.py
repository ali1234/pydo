import os

from pydo import *

from .. import usercommand

@command
def subcommand():
    pass

@command
def other_subcommand():
    usercommand()