from typing import Dict, Any
from kedro.io.core import AbstractDataSet

try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new import Run
    from neptune.new.types import File
    from neptune.new.internal.utils import verify_type
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.types import File
    from neptune.internal.utils import verify_type


from neptune.new import Run


class NeptuneMetadataDataSet(AbstractDataSet):
    def __init__(
            self,
            run: Run
    ):
        self._run = run

    def _save(self, data: Dict[str, Any]) -> None:
        print("ONLY TESTING", data)
        # run = neptune.init(monitoring_namespace='monitoring', source_files=[])
        # for key, value in data.items():
        #     if not isinstance(value, tuple):
        #         value = (value, 'assign')
        #
        #     val, func = value[0], value[1]
        #     getattr(run[key], func)(val)

    def _describe(self) -> Dict[str, Any]:
        print("DESCRIBE")
        return {}

    def _load(self) -> Run:
        print('LOADING')
        return self._run
