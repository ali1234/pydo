import pathlib

from pydo import *

this_dir = pathlib.Path(__file__).parent

input = this_dir / 'input.txt'
output = this_dir / 'output.txt'

@command(produces=[output], consumes=[input])
def build():
    '''
    Help for build command goes here.
    '''
    call([
        f'cp {input} {output}',
    ])

