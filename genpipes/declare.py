import functools
from typing import Any, Callable, List
import types


def generator(inputs: List = None) -> Callable:
    """Decorator function to put value from a decorated function into a stream.
    Forward inputs tas positional args to decorated function
    """
    if not inputs:
        inputs = []

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(stream: types.GeneratorType, **kwargs) -> Any:

            yield from stream  # pulling the value unchanged from the stream
            if isinstance(func(*inputs, **kwargs), types.GeneratorType):
                yield from func(*inputs, **kwargs)
            else:
                value = func(*inputs, **kwargs)
                yield value

        return wrapper

    return decorator


def processor(inputs: List = None) -> Callable:
    """Decorator function to declare function that need value from the stream.
    Forward any inputs to decorated function"""
    if not inputs:
        inputs = []

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(stream: types.GeneratorType, **kwargs) -> Any:
            yield from func(stream, *inputs, **kwargs)

        return wrapper

    return decorator
