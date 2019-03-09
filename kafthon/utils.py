def get_cls_path(cls):
    if not isinstance(cls, type):
        cls = type(cls)
    return f'{cls.__module__}-{cls.__name__}'


def check_type_is_optional(target_type):
    union_args = getattr(
        target_type,
        '__union_params__',  # Python 3.5
        getattr(
            target_type,
            '__args__',  # Python 3.6+
            ()
        )
    )

    is_optional = type(None) in union_args
    return is_optional


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
