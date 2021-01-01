![alt](https://img.shields.io/github/workflow/status/Mg30/genpipes/genpipes-tests)
[![Downloads](https://pepy.tech/badge/genpipes)](https://pepy.tech/project/genpipes)
# Genpipes
Library to write readable and reproductible pipelines using decorators and generators.
Tested for Python > 3.6.9.

## Installation
`pip install genpipes`

## Usage

Below some use case on how to use the library.
### Quick Start

This quick start assume that you have pandas installed as dependency in you project.

```python

import pandas as pd
from genpipes import declare, compose
from collections.abc import Iterable

@declare.generator()
@declare.datasource(inputs=["some_file.csv"])
def data_to_be_processed(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


@declare.processor(inputs=["col1"])
def filter_by(stream: Iterable[pd.DataFrame], col_to_filter:str, value:str):
    for df in stream:
        dff = df[df[col_to_filter] == value]
        yield dff

pipe = compose.Pipeline(steps=[
    ("fetching datasource from some csv file", data_to_be_processed, {}),
    ("performing some filtering based on col1", filter_by, {"value": "some_value"} )
])

output = pipe.run()
```

### Declaring a data source
The first task in data processing is usally to write code to acquire data. The library provide a decorator to declare your data source so they can be easily shared and readable.

The decorators take in a list of inputs to be passed as positional arguments to the decorated function. This way you are binding arguments to the function but you are not hardcoding arguments inside the function.

```python
# my_datasource.py
import pandas as pd
from genpipes import declare

@declare.datasource(inputs=["some_file.csv"])
def data_to_be_processed(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

# other_file.py
from my_datasource import data_to_be_processed

df = data_to_be_processed()
```

However if you want to let some arguments be defined later you could use keywords arguments like so :

```python
# my_datasource.py
import pandas as pd
from genpipes import declare

@declare.datasource(inputs=["some_file.csv"])
def data_to_be_processed(path:str, read_options:dict) -> pd.DataFrame:
    df = pd.read_csv(path, **read_options)
    return df

# other_file.py
from my_datasource import data_to_be_processed

df = data_to_be_processed(read_options={"encoding":"latin1"})

```

### Declaring generator

`generator` decorator is use to initialize a stream.  **Function decorated are transformed to a Python generator object**. You can decorate any function like a `@datasource`.

```python

import pandas as pd
from genpipes import declare, compose

@declare.generator()
@declare.datasource(inputs=["some_file.csv"])
def data_to_be_processed(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df
```

Or a more complexe function

```python
import pandas as pd
from genpipes import declare, compose

@declare.datasource(inputs=["some_file.csv"])
def data_one(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

@declare.datasource(inputs=["some_file_bis.csv"])
def data_two(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


@declare.generator(inputs=[data_one, data_two])
def merging_data(input_one:Callable, input_two:Callable) -> pd.DataFrame:
    df_one = input_one()
    df_two = input_two()
    df_merged = df_one.merge(df_two, on="key")
    return df_merged

```
Decorated function will not received the value from the stream. But the wrapper does receive the value from stream and push it downstream unchanged. 

That's why when calling  your function once decorated you have to pass it as first argument a generator object, so if you want to test you function you can do like that:
```python

empty_stream = () # use to feed the generator decorated function

gen = merging_data(empty_stream)

df_merge = next(gen)# consumming merging_data

```
Because the decorator returns a function that create a generator object you can create many generator object and feed several consumers.

```python
empty_stream = () # use to feed the generator decorated function

gen_one = merging_data(empty_stream)
gen_two = merging_data(empty_stream)

# multiple consuming
consumer_one = next(gen_one)
consumer_two = next(gen_two)

assert consumer_one.equals(consumer_two) # True
```


### Declaring processing functions

Now that we have seen how to declare data sources and how to generate a stream thanks to generator decorator. Let's see how to declare processing functions.

```python
import pandas as pd
from genpipes import declare, compose

@declare.datasource(inputs=["some_file.csv"])
def data_one(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

@declare.datasource(inputs=["some_file_bis.csv"])
def data_two(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


@declare.generator(inputs=[data_one, data_two])
def merging_data(input_one:Callable, input_two:Callable) -> pd.DataFrame:
    df_one = input_one()
    df_two = input_two()
    df_merged = df_one.merge(df_two, on="key")
    return df_merged

@declare.processor(inputs=[["col1, col2"]])
def deduplicate(stream:Iterable[pd.DataFrame], subset:List):
    for df in stream:
        df_nodup = df[~df.duplicated(subset=[subset])]
        yield df_nodup

```
 As you can see, `processor` decorated function **MUST BE** a generator function that take as first argument a generator that represent the stream of values.

 ### Composing pipelines

 Even if we can use the decorator helper function alone, the library provide a `Pipeline` class that help to assemble functions decorated with both `generator` and `processor`.

 A pipeline object is compose of steps that are `tuple` with 3 components:  
 1- The description of the step  
 2- The decorated function  
 3- The keywords arguments to forward as dict, if none then empty dict

 ```python
import pandas as pd
from genpipes import compose, declare

@declare.datasource(inputs=["some_file.csv"])
def data_one(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

@declare.datasource(inputs=["some_file_bis.csv"])
def data_two(path:str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

@declare.generator(inputs=[data_one, data_two])
def merging_data(input_one:Callable, input_two:Callable) -> pd.DataFrame:
    df_one = input_one()
    df_two = input_two()
    df_merged = df_one.merge(df_two, on="key")
    return df_merged

@declare.processor()
def deduplicate(stream:Iterable[pd.DataFrame], subset:List):
    for df in stream:
        df_nodup = df[~df.duplicated(subset=[subset])]
        yield df_nodup


pipe = compose.Pipeline(
    steps=[
        ("data source is the merging of data one and data two",merging_data,{}) # empty dict use here as there is no kwargs,
        ("droping dups",deduplicate, {"subset": ["col1"]} ) # forwarding subset as kwarg
    ]
)
```
When declaring pipeline objects we are not evaluating them. For that we need to call the `run` method. The `run` method return the last object pulled out from the stream. In our case it will be the dedup dataframe from the last step.

``` python
dedup_df = pipe.run()
```
We can run the pipeline multiple time, it will re do all the steps:

``` python
dedup_df = pipe.run()
dedup_df_bis = pipe.run()
assert dedup_df.equals(dedup_df_bis) # True
```

pipeline objects can be used in other pipeline instance as a step:

``` python
@declare.processor()
def filtering_df(stream:Iterable[pd.DataFrame]):
    for df in stream:
        dff = df.filter("some expr")
        yield dff

other_pipe = compose.Pipeline(steps=[
    ("take input other pipeline instance",pipe, {} ),
    ("filtering the output of the first pipe", filtering_df, {})
])

output_from_second_pipe = other_pipe.run() # will run the first pipe instance

```
