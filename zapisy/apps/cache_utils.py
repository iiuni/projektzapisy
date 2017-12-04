"""
Implements a convenient way of caching the result
of expensive functions: a simple decorator.
Credits to:
http://james.lin.net.nz/2011/09/08/python-decorator-caching-your-functions/
"""

from django.core.cache import cache
import hashlib

def cache_get_key(*args, **kwargs):
    """
    Get cache key for storage. MD5-based.
    """
    serialise = []
    for arg in args:
        serialise.append(str(arg))
    for key, arg in list(kwargs.items()):
        serialise.append(str(key))
        serialise.append(str(arg))
    key = hashlib.md5("".join(serialise)).hexdigest()
    return key

"""
If passed a negative timeout value, this function
will not pass it to Django's cache.set function,
which will cause Django to use the default timeout
set in the CACHES configuration in settings.py
"""
def _cache_decorator_internal(time):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = cache_get_key(fn.__name__, *args, **kwargs)
            result = cache.get(key)
            if result is None:
                result = fn(*args, **kwargs)
                if time is not None and time < 0:
                    cache.set(key, result)
                else:
                    cache.set(key, result, time)
            return result
        return wrapper
    return decorator

def cache_result_for(time):
    """
    Cache the result of a function for a specified
    number of seconds.
    """
    return _cache_decorator_internal(time)


def cache_result(fn):
    """
    Cache the result of a function using
    the default timeout by passing a negative
    timeout value (see _cache_decorator_internal docstring).
    """
    return _cache_decorator_internal(-1)(fn)
