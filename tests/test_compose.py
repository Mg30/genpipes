from collections.abc import Iterable, Iterator

import pytest

from genpipes import Pipeline


def test_source_is_lazy_and_called_once_per_traversal() -> None:
    calls: list[int] = []

    def load() -> Iterator[int]:
        calls.append(1)
        return iter([len(calls)])

    pipeline = Pipeline(load)
    stream = iter(pipeline)
    assert calls == []
    assert list(stream) == [1]
    assert list(pipeline) == [2]
    assert calls == [1, 1]


def test_processor_runs_once_and_changes_the_item_type() -> None:
    calls: list[int] = []

    def render(stream: Iterable[int]) -> Iterator[str]:
        calls.append(1)
        return (str(value) for value in stream)

    pipeline = Pipeline(lambda: iter([1, 2])).then(render)
    assert calls == []
    assert list(pipeline) == ["1", "2"]
    assert calls == [1]


def test_run_returns_last_item_and_does_not_retain_empty_output() -> None:
    values = [1, 42]
    pipeline = Pipeline(lambda: iter(values))
    assert pipeline.run() == 42
    values.clear()
    assert pipeline.run() is None


def test_independent_iterators_and_branches() -> None:
    def double(stream: Iterable[int]) -> Iterator[int]:
        return (value * 2 for value in stream)

    original = Pipeline(lambda: iter([1, 2, 3]))
    doubled = original.then(double)
    first = iter(doubled)
    second = iter(doubled)
    assert next(first) == 2
    assert next(first) == 4
    assert next(second) == 2
    assert list(original) == [1, 2, 3]
    assert list(first) == [6]
    assert list(second) == [4, 6]
    assert list(doubled) == [2, 4, 6]


def test_partial_consumption_only_pulls_requested_items() -> None:
    seen: list[int] = []

    def load() -> Iterator[int]:
        for value in range(3):
            seen.append(value)
            yield value

    pipeline = Pipeline(load)
    stream = iter(pipeline)
    assert next(stream) == 0
    assert seen == [0]
    assert list(pipeline) == [0, 1, 2]
    assert list(stream) == [1, 2]


def test_source_errors_propagate_and_next_run_starts_fresh() -> None:
    fail = True

    def load() -> Iterator[int]:
        yield 1
        if fail:
            raise ValueError("source unavailable")
        yield 2

    pipeline = Pipeline(load)
    with pytest.raises(ValueError, match="source unavailable"):
        pipeline.run()
    fail = False
    assert list(pipeline) == [1, 2]


def test_processor_error_is_not_swallowed() -> None:
    def reject(stream: Iterable[int]) -> Iterator[int]:
        for _ in stream:
            raise ValueError("invalid record")
        return iter(())

    pipeline = Pipeline(lambda: iter([1])).then(reject)
    with pytest.raises(ValueError, match="invalid record"):
        pipeline.run()


def test_sources_can_compose_existing_pipelines() -> None:
    left = Pipeline(lambda: iter([1, 2]))
    right = Pipeline(lambda: iter([3]))

    def combined() -> Iterator[int]:
        yield from left
        yield from right

    pipeline = Pipeline(combined)
    assert list(pipeline) == [1, 2, 3]
    assert list(pipeline) == [1, 2, 3]


def test_yielded_batches_are_not_flattened() -> None:
    batch = ["first", "second"]
    pipeline = Pipeline(lambda: iter([batch]))
    assert list(pipeline) == [batch]
    assert pipeline.run() is batch


def test_strings_are_items_when_explicitly_yielded() -> None:
    pipeline = Pipeline(lambda: iter(["hello", "world"]))
    assert list(pipeline) == ["hello", "world"]
