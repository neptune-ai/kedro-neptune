"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from .pipelines.furthest_planet import create_pipeline as furthest_planet
from .pipelines.moons_classifier import create_pipeline as moons_classifier


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    return {
        "__default__": furthest_planet() + moons_classifier(),
    }
