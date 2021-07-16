import os
import sys
import time
import hashlib
from typing import Dict, Any

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from kedro.io import DataCatalog, AbstractDataSet, MemoryDataSet
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from kedro.framework.hooks import hook_impl
from kedro.framework.session import get_current_session

from kedro_neptune.datasets import AbstractNeptuneDataSet

try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new import Run
    from neptune.new.types import File
    from neptune.new.internal.utils import verify_type
    from neptune.new.types import File
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.types import File
    from neptune.internal.utils import verify_type
    from neptune.types import File


from kedro_neptune import __version__
from kedro_neptune.datasets import NeptuneMetadataDataSet


INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'


def log_dataset_metadata(run: Run, base_namespace: str, name: str, dataset: AbstractDataSet):
    run[f'{base_namespace}/datasets/{name}'] = {
        'type': type(dataset).__name__,
        'name': name,
        'filepath': dataset._filepath if hasattr(dataset, '_filepath') else None,
        'version': dataset._version if hasattr(dataset, '_version') else None
    }

    if isinstance(dataset, AbstractNeptuneDataSet):
        file_to_upload = None
        try:
            file_to_upload = File.create_from(dataset.load())
        except TypeError as e:
            pass

        if file_to_upload is None:
            file_to_upload = File(
                content=dataset.load_raw()
            )

        run[f'{base_namespace}/datasets/{name}/data'].upload(file_to_upload)


def log_data_catalog_metadata(run: Run, base_namespace: str, catalog: DataCatalog):
    for name, dataset in catalog._data_sets.items():
        if not isinstance(dataset, MemoryDataSet) and not isinstance(dataset, NeptuneMetadataDataSet):
            log_dataset_metadata(run=run, base_namespace=base_namespace, name=name, dataset=dataset)


def log_pipeline_metadata(run: Run, base_namespace: str, pipeline: Pipeline):
    run[f'{base_namespace}/structure'].upload(File.from_content(pipeline.to_json(), 'json'))


def log_run_params(run: Run, base_namespace: str, run_params: Dict[str, Any]):
    run[f'{base_namespace}/run_params'] = run_params


class NeptuneInit:
    def __init__(self):
        self._timers = {}
        self._neptune_run = None

    @hook_impl
    def after_catalog_created(
            self,
            catalog: DataCatalog,
            conf_catalog: Dict[str, Any],
            conf_creds: Dict[str, Any],
            feed_dict: Dict[str, Any],
            save_version: str,
            load_versions: Dict[str, str],
            run_id: str,
    ) -> None:
        print('CATALOG')
        self._neptune_run = neptune.init(monitoring_namespace='monitoring', source_files=[])
        catalog.add(
            data_set_name='neptune_metadata',
            data_set=NeptuneMetadataDataSet(
                self._neptune_run
            )
        )

    @hook_impl
    def before_pipeline_run(
            self,
            run_params: Dict[str, Any],
            pipeline: Pipeline,
            catalog: DataCatalog
    ) -> None:
        print("PIPELINE")
        session = get_current_session()
        context = session.load_context()
        credentials = context._get_config_credentials()
        config = context.config_loader.get('neptune**')

        os.environ.setdefault('NEPTUNE_API_TOKEN', credentials['neptune']['NEPTUNE_API_TOKEN'] or '')
        os.environ.setdefault('NEPTUNE_PROJECT', config['neptune']['project'] or '')
        os.environ.setdefault('NEPTUNE_CUSTOM_RUN_ID', hashlib.md5(repr(time.time()).encode()).hexdigest())

        base_namespace = config['neptune']['base_namespace'] or 'kedro'
        source_files = config['neptune']['upload_source_files'] or None

        self._neptune_run[INTEGRATION_VERSION_KEY] = run_params.get('kedro_version', __version__)
        self._neptune_run[f'{base_namespace}/kedro_command'] = ' '.join(sys.argv)

        try:
            self._neptune_run[f'{base_namespace}/git'] = Repo().git.rev_parse("HEAD")
        except (InvalidGitRepositoryError, GitCommandError):
            pass

        log_run_params(run=self._neptune_run, base_namespace=base_namespace, run_params=run_params)
        log_data_catalog_metadata(run=self._neptune_run, base_namespace=base_namespace, catalog=catalog)
        log_pipeline_metadata(run=self._neptune_run, base_namespace=base_namespace, pipeline=pipeline)

    @hook_impl
    def before_node_run(
            self,
            node: Node,
            catalog: DataCatalog,
            inputs: Dict[str, Any],
            is_async: bool,
            run_id: str,
    ):
        self._timers[node.short_name] = time.time()
        os.environ['NEPTUNE_MONITORING_NAMESPACE'] = f'monitoring/nodes/{node.short_name}'

    @hook_impl
    def after_node_run(
            self,
            node: Node,
            outputs: Dict[str, Any],
            inputs: Dict[str, Any]
    ) -> None:
        execution_time = time.time() - self._timers[node.short_name]

        session = get_current_session()
        context = session.load_context()
        config = context.config_loader.get('neptune**')

        base_namespace = config['neptune']['base_namespace']

        # run = neptune.init(monitoring_namespace=f'monitoring/nodes/{node.short_name}', source_files=[])
        # run[f'{base_namespace}/nodes/{node.short_name}/outputs'] = list(outputs.keys())
        # run[f'{base_namespace}/nodes/{node.short_name}/inputs'] = list(inputs.keys())
        # run[f'{base_namespace}/nodes/{node.short_name}/execution_time'] = execution_time


neptune_init = NeptuneInit()
