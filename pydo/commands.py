from collections import defaultdict

commands = defaultdict(dict)


def command(f):
    def logger(*args, **kwargs):
        print(f.__name__, f.__module__, *args, **kwargs)
        f(*args, **kwargs)
    commands[f.__module__][f.__name__] = logger
    return logger
