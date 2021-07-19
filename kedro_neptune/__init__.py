#
# Copyright (c) 2021, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__all__ = [
    '__version__',
    'NeptuneMetadataDataSet',
    'neptune_hooks'
]

from kedro.framework.context import KedroContext

from ._version import __version__


import os
import sys
import yaml
import time
import hashlib
from typing import Optional, Dict, Any

import click
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from kedro.io import DataCatalog, AbstractDataSet, MemoryDataSet
from kedro.framework.hooks import hook_impl
from kedro.framework.session import get_current_session, KedroSession
from kedro.framework.project import settings
from kedro.framework.startup import ProjectMetadata
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node


try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new.types import File
    from neptune.new.internal.utils import verify_type
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.types import File
    from neptune.internal.utils import verify_type


INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'


@click.group(name="Neptune")
def commands():
    """Kedro plugin for logging with Neptune.ai"""
    pass


@commands.group(name="neptune")
def neptune_commands():
    pass


@neptune_commands.command()
@click.option('--api-token', prompt='API Token', default=lambda: os.environ.get("NEPTUNE_API_TOKEN", "ANONYMOUS"))
@click.option('--project', prompt=True, default=lambda: os.environ.get("NEPTUNE_PROJECT", "kedro-integration"))
@click.option('--base-namespace', default="kedro")
@click.option('--config', default="base")
@click.pass_obj
def init(metadata: ProjectMetadata, api_token: str, project: str, base_namespace: str, config: str):
    session = KedroSession(metadata.package_name)
    context = session.load_context()

    context.credentials_file = context.project_path / settings.CONF_ROOT / 'local' / "credentials_neptune.yml"

    if not context.credentials_file.exists():
        with context.credentials_file.open("w") as credentials_file:
            yaml.dump({
                    'neptune': {
                        'NEPTUNE_API_TOKEN': api_token
                    }
                },
                credentials_file, default_flow_style=False)

    context.config_file = context.project_path / settings.CONF_ROOT / config / "neptune.yml"

    if not context.config_file.exists():
        with context.config_file.open("w") as config_file:
            yaml.dump({
                'neptune': {
                    'base_namespace': base_namespace,
                    'project': project,
                    'upload_source_files': ['**/*.py',  f'{config}/base/*.yml']
                }
            }, config_file, default_flow_style=False)


class NeptuneMetadataDataSet(AbstractDataSet):
    def __init__(self, run_id: str):
        self._run_id: str = run_id
        self._run: Optional[neptune.Run] = None

    def _save(self, data: Dict[str, Any]) -> None:
        assert self._run is not None

        self._run.assign(data)

    def _describe(self) -> Dict[str, Any]:
        return getattr(self._run, 'get_structure', {})

    def _load(self) -> neptune.Run:
        if not self._run:
            session = get_current_session()
            context = session.load_context()
            credentials = context._get_config_credentials()
            config = context.config_loader.get('neptune**')

            self._run = neptune.init(api_token=credentials['neptune']['NEPTUNE_API_TOKEN'],
                                     project=config['neptune']['project'],
                                     custom_run_id=self._run_id,
                                     source_files=config['neptune']['upload_source_files'] or None)

        return self._run


def log_parameters(namespace: neptune.run.Handler, catalog: DataCatalog):
    namespace['parameters'] = catalog._data_sets['parameters'].load()


def log_dataset_metadata(namespace: neptune.run.Handler, name: str, dataset: AbstractDataSet):
    namespace[name] = {
        'type': type(dataset).__name__,
        'name': name,
        **dataset._describe()
    }


def log_data_catalog_metadata(namespace: neptune.run.Handler, catalog: DataCatalog):
    log_parameters(namespace=namespace, catalog=catalog)

    namespace = namespace['datasets']
    for name, dataset in catalog._data_sets.items():
        if not isinstance(dataset, MemoryDataSet) and not isinstance(dataset, NeptuneMetadataDataSet):
            log_dataset_metadata(namespace=namespace, name=name, dataset=dataset)


def log_pipeline_metadata(namespace: neptune.run.Handler, pipeline: Pipeline):
    namespace['structure'].upload(File.from_content(pipeline.to_json(), 'json'))


def log_run_params(namespace: neptune.run.Handler, run_params: Dict[str, Any]):
    namespace['run_params'] = run_params


def log_git_sha(namespace: neptune.run.Handler):
    try:
        namespace['git'] = Repo().git.rev_parse("HEAD")
    except (InvalidGitRepositoryError, GitCommandError):
        pass


def log_integration_version(run: neptune.Run, run_params: Dict[str, Any]):
    run[INTEGRATION_VERSION_KEY] = run_params.get('kedro_version', __version__)


def log_command(namespace: neptune.run.Handler):
    namespace['kedro_command'] = ' '.join(sys.argv)


class NeptuneHooks:
    def __init__(self):
        self._run_id: Optional[str] = None
        self._neptune_metadata: Optional[NeptuneMetadataDataSet] = None
        self._base_namespace: str = 'kedro'

        self._node_execution_timers: Dict[str, float] = {}

    @property
    def base_namespace(self) -> str:
        return self._base_namespace

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
        self._run_id = hashlib.md5(run_id.encode()).hexdigest()

        self._neptune_metadata = NeptuneMetadataDataSet(self._run_id)
        catalog.add(
            data_set_name='neptune_metadata',
            data_set=self._neptune_metadata
        )

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
        os.environ.setdefault('NEPTUNE_CUSTOM_RUN_ID', self._run_id)

        self._base_namespace = config['neptune']['base_namespace'] or 'kedro'

        neptune_run = self._neptune_metadata.load()
        current_namespace = neptune_run[self.base_namespace]

        log_integration_version(run=neptune_run, run_params=run_params)
        log_command(namespace=current_namespace)
        log_git_sha(namespace=current_namespace)
        log_run_params(namespace=current_namespace, run_params=run_params)
        log_data_catalog_metadata(namespace=current_namespace, catalog=catalog)
        log_pipeline_metadata(namespace=current_namespace, pipeline=pipeline)

    @hook_impl
    def before_node_run(
            self,
            node: Node,
            catalog: DataCatalog,
            inputs: Dict[str, Any],
            is_async: bool,
            run_id: str,
    ):
        neptune_run = self._neptune_metadata.load()
        current_namespace = neptune_run[f'{self.base_namespace}/nodes/{node.short_name}']

        if inputs:
            current_namespace['inputs'].log(list(sorted(inputs.keys())))

        for input_name, input_value in inputs.items():
            if input_name.startswith('params:'):
                current_namespace[f'parameters/{input_name[len("params:"):]}'] = input_value

        os.environ['NEPTUNE_MONITORING_NAMESPACE'] = f'monitoring/nodes/{node.short_name}'
        self._node_execution_timers[node.short_name] = time.time()

    @hook_impl
    def after_node_run(
            self,
            node: Node,
            outputs: Dict[str, Any],
            inputs: Dict[str, Any]
    ) -> None:
        execution_time = float(time.time() - self._node_execution_timers[node.short_name])

        neptune_run = self._neptune_metadata.load()
        current_namespace = neptune_run[f'{self.base_namespace}/nodes/{node.short_name}']

        if outputs:
            current_namespace['outputs'].log(list(sorted(outputs.keys())))
        current_namespace['execution_time'] = execution_time


neptune_hooks = NeptuneHooks()
