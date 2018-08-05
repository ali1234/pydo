from setuptools import setup

setup(
    name='pydo',
    version='',
    packages=['pydo'],
    url='https://github.com/ali1234/pydo',
    license='GPLv3',
    author='Alistair Buxton',
    author_email='a.j.buxton@gmail.com',
    description='A metabuild automation system.',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pydo = pydo.__main__:main'
        ]
    },
)
