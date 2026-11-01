"""Composable, lazy Python data pipelines."""

from genpipes.compose import Pipeline
from genpipes.declare import processor, source

__all__ = ["Pipeline", "processor", "source"]
