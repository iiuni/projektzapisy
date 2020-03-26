from inspect import signature, Parameter
import functools


def auto_assign(func):
    """Assigns values to instance variables automatically
    based on function signature.

    Example:
        # without auto_assign
        class User:
            def __init__(self, name, surname, ...):
                self.name = name
                self.surname = surname
                ...

        # with auto_assign
        class User:
            @auto_assign
            def __init__(self, name, surname, ...):
                pass

    """
    # Signature:
    sig = signature(func)
    for name, param in sig.parameters.items():
        if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
            raise RuntimeError(
                'Unable to auto assign if *args or **kwargs in signature.')

    # Wrapper:
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        for i, (name, param) in enumerate(sig.parameters.items()):
            # Skip 'self' param:
            if i == 0:
                continue
            # Search value in args, kwargs or defaults:
            if i - 1 < len(args):
                val = args[i - 1]
            elif name in kwargs:
                val = kwargs[name]
            else:
                val = param.default
            setattr(self, name, val)
        func(self, *args, **kwargs)
    return wrapper
