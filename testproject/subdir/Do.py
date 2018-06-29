from sh import rm, touch

from pydo import *

@command
def clean(*args):
    rm('-f', 'somefile')

@command
def build(*args):
    touch('somefile')

@command
def all():
    build()
