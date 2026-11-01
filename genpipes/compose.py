"""Lazy, typed pipeline composition."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator


class Pipeline[T]:
    """A reusable definition that creates a fresh stream on each traversal.

    The source must return a new iterator each time it is called. Genpipes
    isolates execution state, but does not copy items or user-owned state.
    """

    __slots__ = ("_source",)

    def __init__(self, source: Callable[[], Iterator[T]]) -> None:
        self._source = source

    def __iter__(self) -> Iterator[T]:
        """Invoke the source once, when consumption starts."""
        yield from self._source()

    def then[U](self, processor: Callable[[Iterable[T]], Iterator[U]]) -> Pipeline[U]:
        """Return a new pipeline with a processor, leaving this one unchanged."""

        def source() -> Iterator[U]:
            return processor(iter(self))

        return Pipeline(source)

    def run(self) -> T | None:
        """Consume this traversal and return its last item, or None if empty."""
        result: T | None = None
        for item in self:
            result = item
        return result
