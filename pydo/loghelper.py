import inspect
import logging
import sys

try:
    import colors
except ImportError:
    colors = False


def findlogger(f):
    cmd_logger = logging.getLogger('command')
    def _inner(*args, **kwargs):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = f'{module.__name__.partition(".")[2]}:{frame.function}'
        logger = logging.LoggerAdapter(cmd_logger, {'command': name, '_lineno': frame.lineno})
        return f(logger, *args, **kwargs)
    return _inner


def l2c(level):
    colours = {
        logging.CRITICAL: {'fg': 'red'},
        logging.ERROR: {'fg': 'orange'},
        logging.WARNING: {'fg': 'yellow'},
        logging.INFO: {'fg': 'green'},
        logging.DEBUG: {'fg': 'blue'},
    }
    return colours[next(x for x in colours.keys() if x <= level)]


class CoreFm(logging.Formatter):
    def format(self, record):
        return f'{record.levelname.title()}: {record.msg}'


class CoreFmColour(logging.Formatter):
    def format(self, record):
        return f'{colors.color(record.levelname.title(), **l2c(record.levelno))}: {colors.color(record.msg, fg="white")}'


class CmdFm(logging.Formatter):
    def format(self, record):
        command = f'{record._module.__name__}:{record._function.__name}:{record._lineno}'
        return f'{record.levelname.title()}: {record.msg}'


class CmdFmColour(logging.Formatter):
    def format(self, record):
        command = f'{record.command}:{record._lineno}'
        return f'{colors.color(command, **l2c(record.levelno))}: {colors.color(record.msg, fg="white")}'


def config(debug, colour):
    core_logger = logging.getLogger('core')
    core_logger.propagate = False
    core_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    core_handler = logging.StreamHandler()
    core_handler.setFormatter(CoreFmColour() if colour else CoreFm())
    core_logger.addHandler(core_handler)

    cmd_logger = logging.getLogger('command')
    cmd_logger.propagate = False
    cmd_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    cmd_handler = logging.StreamHandler()
    cmd_handler.setFormatter(CmdFmColour() if colour else CmdFm())
    cmd_logger.addHandler(cmd_handler)
