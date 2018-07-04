Pydo - how it works.

Pydo is a metabuild automation tool designed to make building large projects
easier. Pydo does not know anything about building software and only deals
with actions, checks and dependencies.

Pydo uses files called Dofiles. Each directory of a project where some action
takes place should have a Dofile. The top level directory of the project must
have an empty file called Do.top to define the project root.

Pydo builds a virtual package `pydo.project` which is anchored to the project
root, and modules are named after the directory they are in.

An example project might look like this:

```
myproject      - imported as:
 + Do.top
 + Dofile      = 'pydo.project'
 + a/
 | | Dofile    = 'pydo.project.a'
 | + subdir/
 |   + Dofile  = 'pydo.project.a.subdir'
 + b/
   + Dofile    = 'pydo.project.b
```

A Dofile can import any standard python module and use it. It can define objects
and functions like a standard python module, and it can import other Dofiles
from the same project using either relative imports or the 'pydo.project'
package.

Dofiles also have some special features not present in a normal module. These
features are accessed by importing `pydo.this_module`. This is a function
which returns a reference to the current module. It allows access to the special
functions in a way that ensures IDEs can see them. The following functionality
is available:

**dependencies**

Each Dofile can declare dependencies on any other Dofiles in the same project.
For example:

```
from . import a, b

this_module().dependencies = [a, b]
```

Will cause this Dofile to depend on the Dofiles in the subdirectories `a/` and `b/`
relative to this Dofile.

If you do not declare any dependencies in a Dofile it will automatically depend
on all of its immediate subdirectories which contain a Dofile.

**sources and targets**

A Dofile can declare a list of source and target files. Sources are files that
the Dofile needs in order to perform its action. Targets are files produced by
the action. this_module().sources and this_module().targets are lists of str
containing filenames relative to the current Dofile's dirrectory.

If no sources are declared, the Dofile will automatically gather the lists of
targets from its immediate dependencies.

**@command**

A Dofile can declare commands which the user can run using the `@command`
decorator. A function decorated this way will be available to run on the
command line when Pydo is run from the Dofile's directory.

```
@command
def usercommand():
    print('hello')
```
```
$ pydo usercommand
hello
```

When before running a command, pydo changes the current working dir to the
Dofile's directory. This also happens if a command is invoked directly from
another module.

Dofiles have some special commands which can't be run directly from the command
line. These are `build` and `check`.

The `build` command is the main action of the Dofile. This is where you tell
Pydo how to build whatever is needed. If not defined in the Dofile, it is
equal to `lambda: None`.

The `check` command tells Pydo whether the current Dofile needs to be re-built
or not. It should return `True` if the Dofile needs to be built. If not declared
it will check the timestamps of `this_module().sources` and `this_module().targets`
to determine if building is necessary. If the Dofile has no sources it uses the
automatic sources. If the Dofile has no targets it returns True.

Both commands should be decorated with `@command` like a user command.

When you run `pydo build` or `pydo check`, Pydo does not directly run the
commands from the current directory Dofile. Instead it builds a list of
recursive dependencies and acts on them in dependency order. `pydo check`
simply prints a list of Dofiles that need to be built in order to build the
current directory Dofile. `pydo build` runs the `check` command from each
dependency and if it returns True, runs `build` on the Dofile, then finally
runs `check` on the current directory Dofile and `build` if necessary.

Other caveats:

Im order to make the above work, there are some things you can't do in a Dofile
that you would be able to do in normal python:

1. You can't define a function called `build` or `check` without decorating it
with `@command`. Pydo will raise an AttributeError if you do this.

2. You can't use various var names in the module scope, such as `dependencies`.
Pydo will raise an AttributeError if you do this. If you wanted to set the
Dofile dependencies, use `this_module().dependencies`. Otherwise, think of another
name for your variable.

Use of the `global` keyword in Dofiles is STRONGLY discouraged, as it allows
you to go around the above restrictions, with undefined results.




