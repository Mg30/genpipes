"""Typed argument binding for sources and stream processors."""

from collections.abc import Callable, Iterable, Iterator
from functools import wraps
from typing import Concatenate

from genpipes.compose import Pipeline


def source[**P, T](func: Callable[P, Iterator[T]]) -> Callable[P, Pipeline[T]]:
    """Turn an iterator factory into a lazy pipeline factory.

    Call the decorated function with its normal arguments to bind them.
    The underlying function runs only when the resulting pipeline is consumed.
    Use yield for one item or batch, and yield from for multiple items.
    """

    @wraps(func)
    def bind(*args: P.args, **kwargs: P.kwargs) -> Pipeline[T]:
        return Pipeline(lambda: func(*args, **kwargs))

    return bind


def processor[T, U, **P](
    func: Callable[Concatenate[Iterable[T], P], Iterator[U]],
) -> Callable[P, Callable[[Iterable[T]], Iterator[U]]]:
    """Bind a processor's arguments, leaving its upstream iterable unbound.

    The decorated function's first argument is the input stream. Calling the
    decorator result supplies the remaining arguments and returns a callable
    suitable for Pipeline.then().
    """

    @wraps(func)
    def bind(*args: P.args, **kwargs: P.kwargs) -> Callable[[Iterable[T]], Iterator[U]]:
        def process(stream: Iterable[T]) -> Iterator[U]:
            return func(stream, *args, **kwargs)

        return process

    return bind
