# Would you like to know more? https://stackoverflow.com/a/6798042/4890123
# Would you like to know even more? https://stackoverflow.com/a/59328423/4890123

_nop_init = lambda self, *args, **kw: None


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        # Python 2 have to check in the cls.__dict__ - Py3 could check the attribute directly:
        elif cls.__init__ is not _nop_init:
            cls.__init__ = _nop_init
        return cls._instance


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
