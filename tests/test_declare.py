from collections.abc import Iterable, Iterator

from genpipes import processor, source


def test_source_binds_arguments_without_evaluating() -> None:
    calls: list[int] = []

    @source
    def numbers(count: int, *, start: int = 0) -> Iterator[int]:
        calls.append(1)
        return iter(range(start, start + count))

    pipeline = numbers(2, start=10)
    assert calls == []
    assert list(pipeline) == [10, 11]
    assert list(pipeline) == [10, 11]
    assert calls == [1, 1]


def test_processor_binds_positional_and_keyword_arguments() -> None:
    calls: list[int] = []

    @source
    def numbers() -> Iterator[int]:
        yield from [1, 2]

    @processor
    def transform(
        stream: Iterable[int], multiplier: int, *, offset: int = 0
    ) -> Iterator[int]:
        calls.append(1)
        return (value * multiplier + offset for value in stream)

    step = transform(3, offset=1)
    pipeline = numbers().then(step)
    assert calls == []
    assert list(pipeline) == [4, 7]
    assert list(pipeline) == [4, 7]
    assert calls == [1, 1]


def test_bound_processor_can_be_reused_directly() -> None:
    @processor
    def render(stream: Iterable[int], prefix: str) -> Iterator[str]:
        for value in stream:
            yield f"{prefix}{value}"

    step = render("item:")
    assert list(step([1, 2])) == ["item:1", "item:2"]
    assert list(step([3])) == ["item:3"]


def test_decorators_preserve_documentation() -> None:
    @source
    def numbers() -> Iterator[int]:
        """Generate numbers."""
        yield 1

    @processor
    def identity(stream: Iterable[int]) -> Iterator[int]:
        """Forward numbers."""
        yield from stream

    assert numbers.__name__ == "numbers"
    assert numbers.__doc__ == "Generate numbers."
    assert identity.__name__ == "identity"
    assert identity.__doc__ == "Forward numbers."
    assert numbers().then(identity()).run() == 1
