# Migrating from genpipes 2.x to 3.x

Version 3 requires Python 3.12+ and replaces the tuple-based composition
interface. Upgrade your code and environment together.

| Version 2 | Version 3 |
| --- | --- |
| `from genpipes import compose, declare` | `from genpipes import Pipeline, source, processor` |
| `@declare.generator(inputs=[...])` | `@source`; bind arguments by calling the decorated function |
| Source returns a scalar or batch | Source explicitly yields the scalar or batch |
| Generator results are detected and flattened | Source always returns an iterator; use `yield from` explicitly |
| `@declare.processor(inputs=[...])` | `@processor`; bind arguments before passing it to `.then(...)` |
| `Pipeline(steps=[(name, function, kwargs), ...])` | `source_function(...).then(processor_function(...))` |
| `prepare()`, `stream`, `output`, `steps`, `names` | Removed; keep the pipeline definition and consume a fresh iterator |
| `pipeline["step name"]` and named-step representation | Removed; retain the source/processor callable directly |
| `pipeline(upstream)` to insert a sub-pipeline | Reuse a prefix with `.then(...)`, or `yield from pipeline` inside a source |
| Poetry / Black / Flake8 | uv / Ruff; strict mypy checks the public interface |

These are intentional removals, without compatibility aliases or implicit
fallbacks.

## Source and processor conversion

Before:

```python
from genpipes import compose, declare


@declare.generator(inputs=[3])
def values(stop):
    return list(range(stop))


@declare.processor(inputs=[10])
def multiply(stream, factor):
    for batch in stream:
        yield [value * factor for value in batch]


pipeline = compose.Pipeline(steps=[("load", values, {}), ("multiply", multiply, {})])
result = pipeline.run()
```

After, preserving the batch semantics:

```python
from collections.abc import Iterable, Iterator

from genpipes import processor, source


@source
def values(stop: int) -> Iterator[list[int]]:
    yield list(range(stop))


@processor
def multiply(stream: Iterable[list[int]], factor: int) -> Iterator[list[int]]:
    for batch in stream:
        yield [value * factor for value in batch]


pipeline = values(3).then(multiply(10))
assert pipeline.run() == [0, 10, 20]
```

To process individual integers instead, use `yield from range(stop)` and a
processor accepting `Iterable[int]`. A source returning a list directly no
longer has a supported source signature; explicitly choose items or batches.

## Arguments and types

Pass source arguments normally: `values(3)`. Pass processor configuration
normally: `multiply(10)`. The upstream iterable is supplied by `.then(...)`
as the first positional argument. Bind other positional and keyword arguments
through the decorated factory; do not pass a separate kwargs dictionary.

Keep the source return annotation as `Iterator[T]` and the processor input as
`Iterable[T]`. Decorators preserve configuration parameter types, and
composition carries the output type into the next stage. Plain functions with
the same stream contract are also supported; decorators are optional.

## Repeatability and failures

The old implementation could invoke a source twice, retain the previous output
after an empty run, or assemble stages again after `prepare()`. Version 3 calls
a reached source once per traversal and keeps all iterator/result state local.
Remove explicit preparation calls.

`run()` still returns only the last item, with `None` for an empty stream.
Use `list(pipeline)` when you want all items. Return a new iterator from every
source invocation. Repeated traversals may still observe changed external data
or mutable arguments; genpipes does not cache, copy, or retry them.

Exceptions are propagated. Creating another iterator starts the definition
again, rather than resuming a failed run.

## Development

Replace `poetry install` with `uv sync --locked` and `poetry run` with
`uv run`. The committed `uv.lock` replaces `poetry.lock`.
Use `ruff check`, `ruff format --check`, and `mypy` before opening a PR.
