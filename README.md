# Genpipes

Composable Python data pipelines using decorators and generators. Declare data
sources, transform their output as a stream, and assemble reusable pipeline steps.
The library has no runtime dependencies.

## Installation and compatibility

```bash
pip install genpipes
```

Package metadata requires Python **>=3.8,<4.0**. The existing CI configuration
lists Python 3.8–3.11, but uses the retired `ubuntu-18.04` runner; it does not
establish current test results or compatibility with newer Python versions.
The package version is 2.0.1. Pandas is optional and only needed for DataFrame examples.

## Quick start

This example runs without external files or third-party dependencies:

```python
from genpipes import compose, declare


@declare.generator()
def orders():
    return [
        {"id": 1, "status": "ready"},
        {"id": 2, "status": "pending"},
        {"id": 3, "status": "ready"},
    ]


@declare.processor(inputs=["ready"])
def filter_status(stream, status):
    for batch in stream:
        yield [order for order in batch if order["status"] == status]


pipeline = compose.Pipeline(steps=[
    ("load orders", orders, {}),
    ("keep ready orders", filter_status, {}),
])

result = pipeline.run()
assert [order["id"] for order in result] == [1, 3]
```

A step is a three-element tuple: a description, a callable, and a dictionary of
keyword arguments. Constructing a pipeline does not execute it. `run()` consumes
the stream and returns its **last emitted value**, not a list of all values.

## Data sources

`@declare.generator(inputs=[...])` binds positional arguments to a source. Step
keyword arguments are forwarded to that source when the stream is consumed.
The wrapper first forwards upstream values, then yields the source's result.
If the source returns a generator, its values are yielded individually.

For a CSV source, install pandas separately and provide an existing CSV file:

```python
import pandas as pd
from genpipes import declare


@declare.generator(inputs=["orders.csv"])
def read_orders(path, encoding="utf-8"):
    return pd.read_csv(path, encoding=encoding)


# Decorated sources require an upstream iterable, even when called directly.
frame = next(read_orders((), encoding="utf-8"))
```

In a pipeline, use `("read CSV", read_orders, {"encoding": "utf-8"})`;
`Pipeline` supplies the upstream iterable.

Source functions should avoid side effects: the current `generator` wrapper may
invoke a source more than once while evaluating its result.

## Processing a stream

`@declare.processor()` wraps a generator function whose first argument is the
upstream iterable. Each yielded value becomes input for the next step.

For pandas DataFrames, a deduplication processor can be written as:

```python
from genpipes import declare


@declare.processor()
def deduplicate(stream, subset):
    for frame in stream:
        yield frame.drop_duplicates(subset=subset)
```

Pass column names as a flat list, for example
`("deduplicate orders", deduplicate, {"subset": ["id"]})`.

## Composing pipelines

Pipelines are callable and can serve as steps in other pipelines. Continuing the
quick-start example:

```python
@declare.processor()
def count_orders(stream):
    for batch in stream:
        yield len(batch)


summary = compose.Pipeline(steps=[
    ("ready orders", pipeline, {}),
    ("count", count_orders, {}),
])

assert summary.run() == 2
```

Calling `run()` again evaluates the steps again. Genpipes does not provide
scheduling, persistence, retries, or distributed execution.

## Development

```bash
poetry install
poetry run pytest
```

## License

[GPL-3.0](LICENSE).
