from collections import defaultdict

commands = defaultdict(dict)

def command(f):
    commands[f.__module__][f.__name__] = f
    return f
