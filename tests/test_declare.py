from genpipes import __version__
from genpipes import declare
import pytest


def test_version():
    assert __version__ == "0.1.1"


@pytest.fixture
def empty_stream():
    stream = ()
    return stream


@pytest.fixture
def fake_stream():
    stream = (i for i in range(0, 1))
    return stream


@pytest.fixture
def fake_stream_bis():
    stream = (i for i in range(0, 1))
    return stream


def test_datasource_inputs():
    inputs = ["is passed"]

    @declare.datasource(inputs=inputs)
    def some_function(positinal_input):
        return positinal_input

    assert some_function() == inputs[0]


def test_datasource_inputs_named():
    inputs = ["is passed"]
    named_args = {"named_args": 0}

    @declare.datasource(inputs=inputs)
    def some_function(positinal_input, named_args: int):
        return positinal_input, named_args

    postional, kwargs = some_function(**named_args)
    assert postional == inputs[0]
    assert kwargs == named_args["named_args"]


def test_datasource_no_inputs():
    @declare.datasource()
    def some_function():
        return True

    assert some_function()


def test_generator_inputs(empty_stream):
    inputs = ["is passed"]

    @declare.generator(inputs=inputs)
    def some_function(positinal_input):
        return positinal_input

    stream = some_function(empty_stream)
    value = next(stream)
    assert value == inputs[0]


def test_generator_inputs_named(empty_stream):
    inputs = ["is passed"]
    named = {"named_args": 0}

    @declare.generator(inputs=inputs)
    def some_function(positinal_input, named_args: int = 1):
        return positinal_input, named_args

    stream = some_function(empty_stream, **named)
    positionnal, named_args = next(stream)
    assert positionnal == inputs[0]
    assert named_args == named["named_args"]


def test_generator_no_inputs(empty_stream):
    @declare.generator()
    def some_function():
        return True

    stream = some_function(empty_stream)
    value = next(stream)
    assert value


def test_generator_function_decorated_is_generator(fake_stream, fake_stream_bis):
    @declare.generator()
    def some_function():
        for i in range(0, 10):
            yield i

    stream = some_function(fake_stream)
    value_from_starting_stream = next(stream)
    value_from_function_decorated = next(stream)
    assert value_from_starting_stream == next(fake_stream_bis)
    assert value_from_function_decorated == 0


def test_processor_inputs(fake_stream):
    inputs = ["is passed"]

    @declare.processor(inputs=inputs)
    def some_function(stream, arg):
        for s in stream:
            yield arg

    stream = some_function(fake_stream)
    value = next(stream)
    assert value == inputs[0]


def test_processor_inputs_named(fake_stream):
    inputs = ["is passed"]
    named = {"named_args": 0}

    @declare.processor(inputs=inputs)
    def some_function(stream, arg, named_args: int):
        for s in stream:
            yield arg, named_args

    stream = some_function(fake_stream, **named)
    positional, named_args = next(stream)
    assert positional == inputs[0]
    assert named_args == named["named_args"]


def test_processor_no_inputs(fake_stream, fake_stream_bis):
    @declare.processor()
    def some_function(
        stream,
    ):
        for s in stream:
            yield s

    stream = some_function(fake_stream)
    value = next(stream)
    assert value == next(fake_stream_bis)


def test_multiple_call():
    @declare.generator()
    def gen_value():
        return 1

    @declare.processor()
    def some_function(
        stream,
    ):
        for s in stream:
            yield s

    stream_one = some_function(gen_value(()))
    stream_two = some_function(gen_value(()))
    value_from_stream_one = next(stream_one)
    value_from_stream_two = next(stream_two)
    assert value_from_stream_one == 1
    assert value_from_stream_two == 1