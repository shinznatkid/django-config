import os


class EnvironDict(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def __getattr__(self, attrname):
        full_attr_name = self.prefix + attrname
        if full_attr_name in os.environ:
            return os.environ[full_attr_name]
        raise AttributeError()


def load_configs():
    try:
        configs = __import__('configs')
    except ImportError:
        try:
            configs = EnvironDict('DJANGO_')
        except Exception:
            configs = {}
    return configs
