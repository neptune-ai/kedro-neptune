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
    'neptune_hooks',
    'init'
]

import os
import sys
import json
import time
import hashlib
import urllib.parse
from typing import Any, Dict, Optional

import click
from ruamel.yaml import YAML
from kedro.framework.hooks import hook_impl
from kedro.framework.project import settings
from kedro.framework.session import KedroSession, get_current_session
from kedro.framework.startup import ProjectMetadata
from kedro.io import DataCatalog, MemoryDataSet
from kedro.io.core import (
    AbstractDataSet,
    get_filepath_str,
    Version,
)
from kedro.extras.datasets.text import TextDataSet
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node

from ._version import __version__

try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new.types import File
    from neptune.new.internal.utils import verify_type
    from neptune.new.internal.utils.paths import join_paths
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.types import File
    from neptune.internal.utils import verify_type
    from neptune.internal.utils.paths import join_paths

INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'


@click.group(name="Neptune")
def commands():
    """Kedro plugin for logging with Neptune.ai"""


@commands.group(name="neptune")
def neptune_commands():
    pass


INITIAL_NEPTUNE_CONFIG = """\
neptune:
#GLOBAL CONFIG
    project: ''
    base_namespace: 'kedro'
    
#LOGGING
    upload_source_files: []
"""


INITIAL_NEPTUNE_CREDENTIALS = """\
neptune:
  NEPTUNE_API_TOKEN: ''
"""


INITIAL_NEPTUNE_CATALOG = """\
# example_artifact:
#   type: kedro_neptune.NeptuneFileDataSet
#   filepath: data/model.pkl
"""


@neptune_commands.command()
@click.option('--api-token', prompt='API Token', default=lambda: os.environ.get("NEPTUNE_API_TOKEN"))
@click.option('--project', prompt=True, default=lambda: os.environ.get("NEPTUNE_PROJECT"))
@click.option('--base-namespace', default="kedro")
@click.option('--config', default="base")
@click.pass_obj
def init(metadata: ProjectMetadata, api_token: str, project: str, base_namespace: str, config: str):
    session = KedroSession(metadata.package_name)
    context = session.load_context()

    yaml = YAML()
    context.credentials_file = context.project_path / settings.CONF_ROOT / 'local' / "credentials_neptune.yml"

    if not context.credentials_file.exists():
        with context.credentials_file.open("w") as credentials_file:
            credentials_template = yaml.load(INITIAL_NEPTUNE_CREDENTIALS)
            credentials_template['neptune']['NEPTUNE_API_TOKEN'] = api_token

            yaml.dump(credentials_template, credentials_file)

            click.echo(f"Created credentials file: {context.credentials_file}")

    context.config_file = context.project_path / settings.CONF_ROOT / config / "neptune.yml"

    if not context.config_file.exists():
        with context.config_file.open("w") as config_file:
            config_template = yaml.load(INITIAL_NEPTUNE_CONFIG)
            config_template['neptune']['project'] = project
            config_template['neptune']['base_namespace'] = base_namespace
            config_template['neptune']['upload_source_files'] = ['**/*.py',  f'{settings.CONF_ROOT}/{config}/*.yml']

            yaml.dump(config_template, config_file)

            click.echo(f"Created config file: {context.config_file}")

    context.catalog_file = context.project_path / settings.CONF_ROOT / config / "catalog_neptune.yml"

    if not context.catalog_file.exists():
        with context.catalog_file.open("w") as catalog_file:
            catalog_file.writelines(INITIAL_NEPTUNE_CATALOG)
            click.echo(f"Created catalog file: {context.catalog_file}")


def get_neptune_config():
    session: KedroSession = get_current_session()
    context = session.load_context()
    # pylint: disable=protected-access
    credentials = context._get_config_credentials()
    config = context.config_loader.get('neptune**')

    api_token = credentials['neptune']['NEPTUNE_API_TOKEN']
    project = config['neptune']['project']
    base_namespace = config['neptune']['base_namespace']
    source_files = config['neptune']['upload_source_files']

    return api_token, project, base_namespace, source_files


class NeptuneMetadataDataSet(AbstractDataSet):
    def _save(self, data: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def _describe(self) -> Dict[str, Any]:
        return {}

    def _exists(self) -> bool:
        return True

    def _load(self) -> neptune.run.Handler:
        api_token, project, base_namespace, _ = get_neptune_config()

        run = neptune.init(api_token=api_token,
                           project=project,
                           capture_stdout=False,
                           capture_stderr=False,
                           capture_hardware_metrics=False,
                           source_files=None)

        return run[base_namespace]


class BinaryFileDataSet(TextDataSet):
    def __init__(
            self,
            filepath: str,
            version: Version = None,
            credentials: Dict[str, Any] = None,
            fs_args: Dict[str, Any] = None,
    ) -> None:
        super().__init__(
            filepath=filepath,
            version=version,
            credentials=credentials,
            fs_args=fs_args
        )

    def _describe(self) -> Dict[str, Any]:
        load_path = get_filepath_str(self._get_load_path(), self._protocol)

        path = urllib.parse.urlparse(load_path).path
        extension = os.path.splitext(path)[1][1:]

        return dict(
            extension=extension,
            **super()._describe()
        )

    def _save(self, data: bytes) -> None:
        path = get_filepath_str(self._get_load_path(), self._protocol)

        with self._fs.open(path, mode='wb') as fs_file:
            return fs_file.write(data)

    def _load(self) -> bytes:
        path = get_filepath_str(self._get_load_path(), self._protocol)

        with self._fs.open(path, mode='rb') as fs_file:
            return fs_file.read()


class NeptuneFileDataSet(BinaryFileDataSet):
    def __init__(
        self,
        filepath: str,
        credentials: Dict[str, Any] = None,
        fs_args: Dict[str, Any] = None,
    ):
        super().__init__(
            filepath=filepath,
            version=None,
            credentials=credentials,
            fs_args=fs_args
        )


def log_file_dataset(namespace: neptune.run.Handler, name: str, dataset: NeptuneFileDataSet):
    # pylint: disable=protected-access
    if not namespace._run.exists(f'{namespace._path}/{name}'):
        data = dataset.load()
        extension = dataset._describe().get('extension')

        try:
            file = File.create_from(data)
        except TypeError:
            file = File.from_content(
                data,
                extension=extension
            )

        namespace[name].upload(
            file
        )


def log_parameters(namespace: neptune.run.Handler, catalog: DataCatalog):
    # pylint: disable=protected-access
    namespace['parameters'] = catalog._data_sets['parameters'].load()


def log_dataset_metadata(namespace: neptune.run.Handler, name: str, dataset: AbstractDataSet):
    additional_parameters = {}
    try:
        # pylint: disable=protected-access
        additional_parameters = dataset._describe()
    except AttributeError:
        pass

    namespace[name] = {
        'type': type(dataset).__name__,
        'name': name,
        **additional_parameters
    }


def log_data_catalog_metadata(namespace: neptune.run.Handler, catalog: DataCatalog):
    # pylint: disable=protected-access
    namespace = namespace['catalog']

    for name, dataset in catalog._data_sets.items():
        if dataset.exists() and not namespace._run.exists(join_paths(namespace._path, name)):
            if not isinstance(dataset, MemoryDataSet) and not isinstance(dataset, NeptuneMetadataDataSet):
                log_dataset_metadata(namespace=namespace['datasets'], name=name, dataset=dataset)

            if isinstance(dataset, NeptuneFileDataSet):
                log_file_dataset(namespace=namespace['files'], name=name, dataset=dataset)

    log_parameters(namespace=namespace, catalog=catalog)


def log_pipeline_metadata(namespace: neptune.run.Handler, pipeline: Pipeline):
    namespace['structure'].upload(File.from_content(
        json.dumps(
            json.loads(pipeline.to_json()),
            indent=4,
            sort_keys=True
        ),
        'json'
    ))


def log_run_params(namespace: neptune.run.Handler, run_params: Dict[str, Any]):
    namespace['run_params'] = run_params


def log_command(namespace: neptune.run.Handler):
    namespace['kedro_command'] = ' '.join(['kedro'] + sys.argv[1:])


class NeptuneHooks:
    def __init__(self):
        self._run_id: Optional[str] = None
        self._node_execution_timers: Dict[str, float] = {}

    # pylint: disable=unused-argument
    @hook_impl
    def after_catalog_created(
            self,
            catalog: DataCatalog,
            run_id: str,
    ) -> None:
        self._run_id = hashlib.md5(run_id.encode()).hexdigest()
        os.environ['NEPTUNE_CUSTOM_RUN_ID'] = self._run_id

        catalog.add(
            data_set_name='neptune_metadata',
            data_set=NeptuneMetadataDataSet()
        )

    @hook_impl
    def before_pipeline_run(
            self,
            run_params: Dict[str, Any],
            pipeline: Pipeline,
            catalog: DataCatalog
    ) -> None:
        api_token, project, base_namespace, source_files = get_neptune_config()

        run = neptune.init(api_token=api_token,
                           project=project,
                           custom_run_id=self._run_id,
                           source_files=source_files or None)

        run[INTEGRATION_VERSION_KEY] = __version__

        current_namespace = run[base_namespace]

        os.environ['NEPTUNE_API_TOKEN'] = api_token or ''
        os.environ['NEPTUNE_PROJECT'] = project or ''

        log_command(namespace=current_namespace)
        log_run_params(namespace=current_namespace, run_params=run_params)
        log_data_catalog_metadata(namespace=current_namespace, catalog=catalog)
        log_pipeline_metadata(namespace=current_namespace, pipeline=pipeline)

    @hook_impl
    def before_node_run(
            self,
            node: Node,
            inputs: Dict[str, Any],
            catalog: DataCatalog
    ):
        run = catalog.load('neptune_metadata')
        current_namespace = run[f'nodes/{node.short_name}']

        if inputs:
            current_namespace['inputs'] = list(sorted(inputs.keys()))

        for input_name, input_value in inputs.items():
            if input_name.startswith('params:'):
                current_namespace[f'parameters/{input_name[len("params:"):]}'] = input_value

        self._node_execution_timers[node.short_name] = time.time()

    @hook_impl
    def after_node_run(
            self,
            node: Node,
            catalog: DataCatalog,
            outputs: Dict[str, Any]
    ) -> None:
        # pylint: disable=protected-access
        execution_time = float(time.time() - self._node_execution_timers[node.short_name])

        run = catalog.load('neptune_metadata')
        current_namespace = run[f'nodes/{node.short_name}']
        current_namespace['execution_time'] = execution_time

        if outputs:
            current_namespace['outputs'] = list(sorted(outputs.keys()))

        log_data_catalog_metadata(namespace=run, catalog=catalog)
        run._run.sync()

    @hook_impl
    def after_pipeline_run(
            self,
            catalog: DataCatalog
    ) -> None:
        # pylint: disable=protected-access
        run = catalog.load('neptune_metadata')
        log_data_catalog_metadata(namespace=run, catalog=catalog)
        run._run.sync()


neptune_hooks = NeptuneHooks()
