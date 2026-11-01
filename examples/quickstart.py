"""Run with: uv run python examples/quickstart.py"""

from collections.abc import Iterable, Iterator
from typing import TypedDict

from genpipes import processor, source


class Order(TypedDict):
    id: int
    status: str


@source
def orders() -> Iterator[Order]:
    yield {"id": 1, "status": "ready"}
    yield {"id": 2, "status": "pending"}
    yield {"id": 3, "status": "ready"}


@processor
def filter_status(stream: Iterable[Order], status: str) -> Iterator[Order]:
    for order in stream:
        if order["status"] == status:
            yield order


pipeline = orders().then(filter_status("ready"))
assert [order["id"] for order in pipeline] == [1, 3]
assert pipeline.run() == {"id": 3, "status": "ready"}
print(list(pipeline))
