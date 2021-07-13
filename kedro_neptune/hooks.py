import os
import time
import hashlib
from typing import Dict, Any

from kedro.io import DataCatalog, AbstractDataSet, MemoryDataSet
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from kedro.framework.hooks import hook_impl
from kedro.framework.session import get_current_session


try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new import Run
    from neptune.new.internal.utils import verify_type
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.internal.utils import verify_type


from kedro_neptune import __version__


INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'


def log_dataset_metadata(run: Run, base_namespace: str, name: str, dataset: AbstractDataSet):
    run[f'{base_namespace}/datasets/{name}'] = {
        'type': type(dataset).__name__,
        'name': name,
        'filepath': dataset._filepath if hasattr(dataset, '_filepath') else None,
        'version': dataset._version if hasattr(dataset, '_version') else None
    }


def log_data_catalog_metadata(run: Run, base_namespace: str, catalog: DataCatalog):
    for name, dataset in catalog._data_sets.items():
        if not isinstance(dataset, MemoryDataSet):
            log_dataset_metadata(run=run, base_namespace=base_namespace, name=name, dataset=dataset)


class NeptuneInit:
    @hook_impl
    def before_pipeline_run(
            self,
            run_params: Dict[str, Any],
            pipeline: Pipeline,
            catalog: DataCatalog
    ) -> None:
        session = get_current_session()
        context = session.load_context()
        credentials = context._get_config_credentials()
        config = context.config_loader.get('neptune**')

        os.environ.setdefault('NEPTUNE_API_TOKEN', credentials['neptune']['NEPTUNE_API_TOKEN'] or '')
        os.environ.setdefault('NEPTUNE_PROJECT', config['neptune']['project'] or '')
        os.environ.setdefault('NEPTUNE_CUSTOM_RUN_ID', hashlib.md5(repr(time.time()).encode()).hexdigest())

        run = neptune.init(monitoring_namespace='monitoring')
        run[INTEGRATION_VERSION_KEY] = run_params.get('kedro_version', __version__)
        log_data_catalog_metadata(run=run, base_namespace=config['neptune']['base_namespace'], catalog=catalog)

    @hook_impl
    def before_node_run(
            self,
            node: Node,
            catalog: DataCatalog,
            inputs: Dict[str, Any],
            is_async: bool,
            run_id: str,
    ):
        os.environ['NEPTUNE_MONITORING_NAMESPACE'] = f'monitoring/{node.short_name}'


neptune_init = NeptuneInit()
