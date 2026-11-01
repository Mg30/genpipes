# Genpipes

Typed, lazy Python data pipelines using decorators and generators. Bind source
arguments, compose stream processors, and consume the result when needed.

Genpipes requires **Python 3.12+** and has **no runtime dependencies**. It provides
synchronous stream composition; scheduling, persistence, retries, and distributed
execution are outside its scope.

## Installation

This branch prepares **3.0.0**, with breaking changes from 2.x. To try v3 before
it is published, install from a checkout of this branch:

```bash
python -m pip install .
```

After the 3.x release is published to PyPI:

```bash
python -m pip install "genpipes>=3,<4"
```

Existing users should read the [v2 to v3 migration guide](docs/migration-v3.md).
The CI matrix covers CPython 3.12–3.15 on Linux.

## Quick start

```python
from collections.abc import Iterable, Iterator

from genpipes import processor, source


@source
def numbers(stop: int) -> Iterator[int]:
    yield from range(stop)


@processor
def multiply(stream: Iterable[int], factor: int) -> Iterator[int]:
    for value in stream:
        yield value * factor


pipeline = numbers(3).then(multiply(10))

assert list(pipeline) == [0, 10, 20]
assert pipeline.run() == 20
assert list(pipeline) == [0, 10, 20]  # A fresh traversal.
```

Calling a decorated source binds its arguments and returns a `Pipeline[T]`.
Calling a decorated processor binds every argument after its upstream iterable;
pass the resulting callable to `.then(...)`. The type checker tracks each
stage's item type and rejects incompatible connections.

Constructing, extending, or obtaining an iterator from a pipeline does not invoke
its source or processors. Execution starts when that iterator is consumed.
Each traversal invokes each reached stage once; processors decide how much of
their upstream stream to consume.

## Items and batches

Sources return iterators. Use `yield` for one item or batch and `yield from`
for multiple items. Genpipes does not guess whether an iterable is a batch.

```python
from collections.abc import Iterator

from genpipes import source


@source
def batches() -> Iterator[list[int]]:
    yield [1, 2, 3]


assert list(batches()) == [[1, 2, 3]]
```

The same rule applies to strings, dictionaries, and pandas DataFrames. For
DataFrame pipelines, install pandas separately and explicitly yield each frame:

```python
from collections.abc import Iterable, Iterator

import pandas as pd

from genpipes import processor, source


@source
def frames() -> Iterator[pd.DataFrame]:
    yield pd.DataFrame({"id": [1, 1, 2]})


@processor
def deduplicate(
    stream: Iterable[pd.DataFrame], subset: list[str]
) -> Iterator[pd.DataFrame]:
    for frame in stream:
        yield frame.drop_duplicates(subset=subset)


result = frames().then(deduplicate(["id"])).run()
assert result is not None
assert result["id"].tolist() == [1, 2]
```

## Composition without decorators

Decorators are argument-binding helpers. A plain source factory and processor
work directly:

```python
from collections.abc import Iterable, Iterator

from genpipes import Pipeline


def load() -> Iterator[int]:
    return iter([1, 2, 3])


def render(stream: Iterable[int]) -> Iterator[str]:
    return (f"item:{value}" for value in stream)


original = Pipeline(load)
rendered = original.then(render)

assert list(original) == [1, 2, 3]
assert list(rendered) == ["item:1", "item:2", "item:3"]
```

`.then(...)` returns a new pipeline, so a prefix can be reused in multiple
branches. To combine existing pipelines, yield from them in a new source:

```python
def combined() -> Iterator[int]:
    yield from original
    yield from original


assert list(Pipeline(combined)) == [1, 2, 3, 1, 2, 3]
```

## Execution contract

- `iter(pipeline)` creates an independent lazy traversal; `list(pipeline)`
  collects all emitted items.
- `run()` consumes a traversal and returns its last item, or `None` if empty.
  An empty stream and a last item of `None` intentionally have the same result.
- A source must create a **fresh iterator per call**. Reusing a captured,
  exhausted iterator does not make its data replayable.
- Pipeline execution state is local to each traversal. Bound arguments and
  emitted objects are not copied; their mutability and external side effects
  remain the caller's responsibility.
- Exceptions propagate to the consumer. A later traversal starts fresh; it does
  not resume or retry the failed traversal.
- Laziness follows the processors you write. A processor that materializes its
  entire input will do so when reached. Manage external resource lifetimes in
  your source/processor code, especially when stopping consumption early.

The public interface is `Pipeline`, `source`, and `processor`, imported from
`genpipes`. The distribution includes `py.typed` for downstream type checking.

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and work from
the repository root:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --cov --cov-report=term-missing
uv run python examples/quickstart.py
uv build --no-sources
uv run twine check --strict dist/*
```

Use `uv run ruff format .` to apply formatting locally. Commit `uv.lock` when
changing development dependencies. CI uses the same locked environment, checks
types and formatting, runs the Python matrix, and tests the built wheel outside
the checkout.

See [release instructions](docs/releasing.md) for the GitHub OIDC/PyPI Trusted
Publishing setup and [CHANGELOG.md](CHANGELOG.md) for v3 changes.

## License

[GNU GPL version 3](LICENSE). The license file is unchanged by v3.
