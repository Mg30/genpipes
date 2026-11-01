from collections.abc import Iterable, Iterator

import pandas as pd

from genpipes import processor, source


def test_dataframe_remains_a_single_batch() -> None:
    @source
    def frames() -> Iterator[pd.DataFrame]:
        yield pd.DataFrame({"id": [1, 1, 2], "value": [10, 10, 20]})

    @processor
    def deduplicate(
        stream: Iterable[pd.DataFrame], subset: list[str]
    ) -> Iterator[pd.DataFrame]:
        for frame in stream:
            yield frame.drop_duplicates(subset=subset)

    results = list(frames().then(deduplicate(["id"])))
    assert len(results) == 1
    assert results[0].to_dict("list") == {"id": [1, 2], "value": [10, 20]}
