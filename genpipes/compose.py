from typing import Any, Callable, Generator, List, Tuple


class Pipeline(object):
    """Class that contains steps representing operations to be sequentially executed.
    Thanks to Generetors Tasks are lazily evaluated until run method is call.
    """

    def __init__(self, steps: List[Tuple[str, Callable]]) -> None:
        self.stream = ()  # empty generator needed to init the stream
        self.steps = steps
        self.output = None
        self.names = []

    def __call__(self, gen) -> Generator:
        """ Implementation of special call method to allow a Pipeline object to receive an other Pipeline object"""
        self.stream = gen
        self.prepare()
        return self.stream

    def __repr__(self) -> str:
        """Implementation of repr to show tasks composing the current pipeline"""
        names = []
        for index, task in enumerate(self.steps):
            names.append(f"{index+1}- {task[0]}")
        tasks = "\n".join(names)
        rpr = f"""---- Start ----
{tasks}
---- End ----
        """
        return rpr

    def __getitem__(self, item):
        founded = False
        i = 0
        step = None
        while not founded and i != len(self.steps) - 1:
            step = self.steps[i]
            founded = step[0] == item
            i += 1
        if founded:
            return step
        else:
            raise KeyError

    def prepare(self) -> None:
        """Preparing the stream of tasks, does not execute the pipeline """
        for name, step, kwargs in self.steps:
            self.stream = step(self.stream, **kwargs)

    def run(self) -> Any:
        """Executing the pipeline and return the last value of it"""
        self.prepare()
        for step in self.stream:
            self.output = step
        return self.output
