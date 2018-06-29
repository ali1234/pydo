import pydo.project
import pydo.project.subdir

print('top imported')

def main():
    print('main')
    pydo.project.subdir.sub()


def blah():
    print('blah')