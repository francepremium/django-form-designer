from importlib import import_module


def import_class(path):
    bits = path.split('.')
    module = '.'.join(bits[:-1])
    cls = bits[-1]
    module = import_module(module)
    return getattr(module, cls)
