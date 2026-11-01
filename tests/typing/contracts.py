"""Consumer contracts; mypy also verifies every expected rejection below."""

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, assert_type

from genpipes import Pipeline, processor, source


@source
def numbers(count: int, *, start: int = 0) -> Iterator[int]:
    yield from range(start, start + count)


@processor
def render(stream: Iterable[int], *, prefix: str = "") -> Iterator[str]:
    for value in stream:
        yield f"{prefix}{value}"


def lengths(stream: Iterable[str]) -> Iterator[int]:
    return (len(value) for value in stream)


pipeline = numbers(2, start=1)
assert_type(pipeline, Pipeline[int])
assert_type(iter(pipeline), Iterator[int])
assert_type(pipeline.run(), int | None)
rendered = pipeline.then(render(prefix="item:"))
assert_type(rendered, Pipeline[str])
assert_type(rendered.then(lengths), Pipeline[int])

if TYPE_CHECKING:
    # warn_unused_ignores makes CI fail if these invalid calls become accepted.
    numbers("two")  # type: ignore[arg-type]
    numbers(2, unknown=1)  # type: ignore[call-arg]
    render(prefix=42)  # type: ignore[arg-type]
    pipeline.then(lengths)  # type: ignore[arg-type]
