from abc import ABC
from typing import Any, Dict

from kedro.io import AbstractVersionedDataSet
from kedro.io.core import parse_dataset_definition

try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune


class AbstractNeptuneDataSet(AbstractVersionedDataSet, ABC):
    """Abstract class for extending other DataSets.
     Instances are produced by NeptuneArtifactDataSet factory."""
    pass


class NeptuneArtifactDataSet(AbstractVersionedDataSet):
    def __new__(cls, dataset: Dict):
        dataset_class, data_set_args = parse_dataset_definition(config=dataset)

        class NeptuneExtendedDataSet(dataset_class, AbstractNeptuneDataSet):
            """This class extends dataset_class.
            It's kind of 'annotation' with information that this `dataset` should be uploaded to neptune."""
            def __init__(self):
                super().__init__(**data_set_args)

        # rename the class
        parent_name = dataset_class.__name__
        NeptuneExtendedDataSet.__name__ = f"NeptuneArtifactDataSetFor{parent_name}"
        NeptuneExtendedDataSet.__qualname__ = f"{cls.__name__}.{NeptuneArtifactDataSet.__name__}"

        return NeptuneExtendedDataSet()

    def _load(self) -> Any:
        raise AttributeError("NeptuneArtifactDataSet is a factory, this function should not be called.")

    def _save(self, data: Any) -> None:
        raise AttributeError("NeptuneArtifactDataSet is a factory, this function should not be called.")

    def _describe(self) -> Dict[str, Any]:
        raise AttributeError("NeptuneArtifactDataSet is a factory, this function should not be called.")
