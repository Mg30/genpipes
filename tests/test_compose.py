import types
from typing import Iterable
from genpipes import __version__
from genpipes import compose, declare
import pandas as pd
import pytest


def test_version():
    assert __version__ == "0.1.0"


@declare.generator()
@declare.datasource()
def fake_dataframe():
    df = pd.DataFrame({"col1": [1, 2, 3, 4, 5, 6], "col2": [1, 2, 3, 4, 5, 6]})
    return df


@declare.processor()
def multiply_by(stream: Iterable[pd.DataFrame], number: int = 2):
    for df in stream:
        cols = df.columns
        for col in cols:
            df[col] = df[col] * number

        yield df


@pytest.fixture
def pipe():
    return compose.Pipeline(
        steps=[
            ("fetching source", fake_dataframe, {}),
            ("multiply by two", multiply_by, {}),
        ]
    )


@pytest.fixture
def pipe_bis():
    return compose.Pipeline(steps=[("fetching source", fake_dataframe, {})])


@pytest.fixture
def expected_output():
    df = pd.DataFrame({"col1": [1, 2, 3, 4, 5, 6], "col2": [1, 2, 3, 4, 5, 6]})
    cols = df.columns
    for col in cols:
        df[col] = df[col] * 2
    return df


def test_pipeline_rpr(pipe):
    assert isinstance(str(pipe), str)


def test_subscriptable(pipe):
    assert pipe["fetching source"] == ("fetching source", fake_dataframe, {})


def test_subscriptable_not_found(pipe):
    with pytest.raises(KeyError):
        pipe["prout"]


def test_callable_pipeline(pipe_bis):
    assert isinstance(pipe_bis(multiply_by), types.GeneratorType)


def test_prepare(pipe):
    pipe.prepare()
    assert isinstance(pipe.stream, types.GeneratorType)


def test_pipeline_output(pipe, expected_output):
    output = pipe.run()
    assert expected_output.equals(output)

def test_pipeline_multiple_run(pipe, expected_output):
    output_one = pipe.run()
    output_two = pipe.run()
    assert expected_output.equals(output_one)
    assert expected_output.equals(output_two)

def test_pipeline_with_another_pipeline_instance(pipe_bis, expected_output):
    composed_pipe = compose.Pipeline(
        steps=[
            ("other pipeline instance", pipe_bis, {}),
            ("multiply by two", multiply_by, {}),
        ]
    )
    df = composed_pipe.run()
    assert df.equals(expected_output)


def test_pipeline_with_another_pipeline_instance_with_kwargs(pipe_bis, expected_output):
    composed_pipe = compose.Pipeline(
        steps=[
            ("other pipeline instance", pipe_bis, {}),
            ("multiply df with provided number", multiply_by, {"number":10}),
        ]
    )
    df = composed_pipe.run()
    assert not df.equals(expected_output)