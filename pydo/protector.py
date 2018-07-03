from pydo.commands import SyntaxCheckerIgnore


class Protector(object):
    def __init__(self, module):
        self._dict = module.__dict__
        self._protected = set(vars(type(module)).keys())

    def __getitem__(self, k):
        if k in self._protected:
            if callable(self._dict[k]):
                raise SyntaxError("'{:s}' is a module instance method. Access it with 'pydo.this_module().{:s}'".format(k, k))
            else:
                raise SyntaxError("'{:s}' is a module instance attribute. Access it with 'pydo.this_module().{:s}'".format(k, k))
        return self._dict[k]

    def __setitem__(self, k, v):
        if k in self._protected:
            if v is SyntaxCheckerIgnore:
                return
            if callable(self._dict[k]):
                raise SyntaxError("'{:s}' is a module instance method. Define it with the '@command' decorator.".format(k, k))
            else:
                raise SyntaxError("'{:s}' is a module instance attribute. Access it with 'pydo.this_module().{:s}'".format(k, k))
        self._dict[k] = v

    def __delitem__(self, k):
        if k in self._protected:
            raise SyntaxError("'{:s}' is a module instance attribute and cannot be deleted.".format(k))
        del self._dict[k]