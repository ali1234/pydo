from sh import rm, touch, ls, pwd

from pydo import *



c = Component()

class MyComponent(Component):
    pass

mc = MyComponent()

@command
def clean(*args):
    rm('-f', 'somefile')

@command
def build(*args):
    print(mc.__module__)
    print(pwd())
    touch('somefile')

@command
def default():
    build()

