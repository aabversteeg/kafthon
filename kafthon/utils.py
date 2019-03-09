def get_cls_path(cls):


def check_is_method(obj):
    return (
        callable(obj) and
        hasattr(obj, '__code__') and
        hasattr(obj.__code__, 'co_varnames') and
        isinstance(obj.__code__.co_varnames, tuple) and  # ensure it is no mock obj
        len(obj.__code__.co_varnames) > 0 and
        obj.__code__.co_varnames[0] == 'self' and
        not hasattr(obj, '__self__')
    )
