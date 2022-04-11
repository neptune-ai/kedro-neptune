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
    'NeptuneRunDataSet',
    'NeptuneFileDataSet',
    'neptune_hooks',
    'init'
]

import hashlib
import json
import os
import sys
import time
import urllib.parse
from typing import Any, Dict, Optional

import click
from kedro.extras.datasets.text import TextDataSet
from kedro.framework.hooks import hook_impl
from kedro.framework.project import settings
from kedro.framework.session import KedroSession
from kedro.framework.startup import ProjectMetadata
from kedro.io import DataCatalog, MemoryDataSet
from kedro.io.core import (
    AbstractDataSet,
    get_filepath_str,
    Version,
)
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from ruamel.yaml import YAML

from kedro_neptune._version import get_versions
from kedro_neptune.config import get_neptune_config

try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new.types import File
    from neptune.new.handler import Handler
    from neptune.new.internal.utils import verify_type
    from neptune.new.internal.utils.paths import join_paths
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.types import File
    from neptune.handler import Handler
    from neptune.internal.utils import verify_type
    from neptune.internal.utils.paths import join_paths

INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'

__version__ = get_versions()['version']


@click.group(name='Neptune')
def commands():
    """Kedro plugin for logging with Neptune.ai"""


@commands.group(name='neptune')
def neptune_commands():
    pass


INITIAL_NEPTUNE_CONFIG = """\
neptune:
#GLOBAL CONFIG
  project: ''
  base_namespace: 'kedro'
  enabled: true

#LOGGING
  upload_source_files:
  # - '**/*.py'
  - 'conf/base/*.yml'
"""

INITIAL_NEPTUNE_CREDENTIALS = """\
neptune:
  api_token: $NEPTUNE_API_TOKEN
"""

INITIAL_NEPTUNE_CATALOG = """\
# You can log files to Neptune via NeptuneFileDataSet
#
# example_artifact:
#   type: kedro_neptune.NeptuneFileDataSet
#   filepath: data/06_models/clf_model.pkl
#
# If you want to log existing Kedro Dataset to Neptune add @neptune to the DataSet name
#
# example_iris_data@neptune:
#   type: kedro_neptune.NeptuneFileDataSet
#   filepath: data/01_raw/iris.csv
#
# You can use kedro_neptune.NeptuneFileDataSet in any catalog including conf/base/catalog.yml
#
"""

PROMPT_API_TOKEN = """Pass Neptune API Token or press enter if you want to \
use $NEPTUNE_API_TOKEN environment variable:""".replace('\n', '')
PROMPT_PROJECT_NAME = """Pass Neptune project name in a WORKSPACE/PROJECT format or press enter if you want to \
use $NEPTUNE_PROJECT environment variable:""".replace('\n', '')


@neptune_commands.command()
@click.option('--api-token', prompt=PROMPT_API_TOKEN, default='$NEPTUNE_API_TOKEN')
@click.option('--project', prompt=PROMPT_PROJECT_NAME, default='$NEPTUNE_PROJECT')
@click.option('--base-namespace', default='kedro')
@click.option('--config', default='base')
@click.pass_obj
def init(metadata: ProjectMetadata, api_token: str, project: str, base_namespace: str, config: str):
    """Command line interface (CLI) command for initializing Kedro-Neptune plugin.

    Kedro-Neptune plugin lets you log metadata related to Kedro pipelines to `Neptune.ai ML metadata store`_
    so that you can monitor, visualize, and compare your pipelines and node outputs in the Neptune UI.

    After initializing it, whenever you run '$ kedro run', you will log:
    * parameters
    * pipeline execution configuration (run_params)
    * metadata about Kedro DataSets
    * hardware consumption and node execution times
    * configuration files from the conf/base directory
    * full Kedro run command
    * any additional metadata like metrics, charts, or images that you logged from inside of your node functions.

    See `example project in Neptune`_.
    You may also want to check `Neptune-Kedro integration docs page`_.
    Args:
        api-token (string:) Neptune API token or the environment variable name where it is stored.
            Default is '$NEPTUNE_API_TOKEN'. See `How to find your Neptune API token`_.
        project (string): Neptune project name or the environment variable name where it is stored.
            Default is '$NEPTUNE_API_TOKEN'. See `How to find your Neptune project name`_.
        base-namespace (string): Namespace in Neptune where all the Kedro-related metadata is logged.
            Default is 'kedro'.
        config (string): Name of the Subdirectory inside of the Kedro 'conf' directory for
            configuration and catalog files. Default is 'base'.
    Returns:
        ``dict`` with all summary items.
    Examples:

        Pass required arguments directly
        $ kedro neptune init --api-token $NEPTUNE_API_TOKEN --project common/kedro-integration

        Use prompts to fill the required arguments
        $ kedro neptune init

    You may also want to check `Neptune-Kedro integration docs page`_.

    .. _Neptune.ai ML metadata store:
        https://neptune.ai/
    .. _example project in Neptune:
        https://app.neptune.ai/o/common/org/kedro-integration/e/KED-572
    .. _Neptune-Kedro integration docs page:
       https://docs.neptune.ai/integrations-and-supported-tools/pipeline-and-orchestration/kedro
    .. _How to find your Neptune project name:
       https://docs.neptune.ai/getting-started/installation#setting-the-project-name
    .. _How to find your Neptune API token:
       https://docs.neptune.ai/getting-started/installation#authentication-neptune-api-token
    """
    session = KedroSession(metadata.package_name)
    context = session.load_context()

    yaml = YAML()
    context.credentials_file = context.project_path / settings.CONF_SOURCE / 'local' / 'credentials_neptune.yml'

    if not context.credentials_file.exists():
        with context.credentials_file.open('w') as credentials_file:
            credentials_template = yaml.load(INITIAL_NEPTUNE_CREDENTIALS)
            credentials_template['neptune']['api_token'] = api_token

            yaml.dump(credentials_template, credentials_file)

            click.echo(f'Created credentials_neptune.yml configuration file: {context.credentials_file}')

    context.config_file = context.project_path / settings.CONF_SOURCE / config / 'neptune.yml'

    if not context.config_file.exists():
        with context.config_file.open('w') as config_file:
            config_template = yaml.load(INITIAL_NEPTUNE_CONFIG)
            config_template['neptune']['project'] = project
            config_template['neptune']['base_namespace'] = base_namespace
            config_template['neptune']['upload_source_files'] = ['**/*.py', f'{settings.CONF_SOURCE}/{config}/*.yml']

            yaml.dump(config_template, config_file)

            click.echo(f'Creating neptune.yml configuration file in: {context.config_file}')

    context.catalog_file = context.project_path / settings.CONF_SOURCE / config / 'catalog_neptune.yml'

    if not context.catalog_file.exists():
        with context.catalog_file.open('w') as catalog_file:
            catalog_file.writelines(INITIAL_NEPTUNE_CATALOG)
            click.echo(f'Creating catalog_neptune.yml configuration file: {context.catalog_file}')


def _connection_mode(enabled: bool) -> str:
    return 'async' if enabled else 'debug'


class NeptuneRunDataSet(AbstractDataSet):
    def _save(self, data: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def _describe(self) -> Dict[str, Any]:
        return {}

    def _exists(self) -> bool:
        return True

    def _load(self) -> Handler:
        config = get_neptune_config(settings)

        run = neptune.init(api_token=config.api_token,
                           project=config.project,
                           mode=_connection_mode(config.enabled),
                           capture_stdout=False,
                           capture_stderr=False,
                           capture_hardware_metrics=False,
                           capture_traceback=False,
                           source_files=None)

        return run[config.base_namespace]


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
    """NeptuneFileDataSet is a Kedro Data Set that lets you log files to Neptune.

    It can be any file on the POSIX compatible filesystem.
    To log it, you need to define the NeptuneFileDataSet in any Kedro catalog, including catalog.yml.

    You may also want to check `Neptune-Kedro integration docs page`_.
    Args:
        filepath (string): Filepath in POSIX format to a text file prefixed with a protocol like s3://.
            Same as for `Kedro TextDataSet`_.
        credentials (dict, optional): Credentials required to get access to the underlying filesystem.
            Same as for `Kedro TextDataSet`_.
        fs_args (dict, optional): Extra arguments to pass into underlying filesystem class constructor.
            Same as for`Kedro TextDataSet`_.
    Examples:
        Log a file to Neptune from any Kedro catalog YML file.

        example_model_file:
            type: kedro_neptune.NeptuneFileDataSet
            filepath: data/06_models/clf.pkl

        Log a file to Neptune that has already been defined as a Kedro DataSet in any catalog YML file.

        example_iris_data:
            type: pandas.CSVDataSet
            filepath: data/01_raw/iris.csv

        example_iris_data@neptune:
            type: kedro_neptune.NeptuneFileDataSet
            filepath: data/01_raw/iris.csv

    You may also want to check `Neptune-Kedro integration docs page`_.
    .. _Neptune-Kedro integration docs page:
       https://docs.neptune.ai/integrations-and-supported-tools/pipeline-and-orchestration/kedro
    .. _Kedro TextDataSet:
        https://kedro.readthedocs.io/en/stable/kedro.extras.datasets.text.TextDataSet.html
    """
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


def log_file_dataset(namespace: Handler, name: str, dataset: NeptuneFileDataSet):
    # pylint: disable=protected-access
    if not namespace.container.exists(f'{namespace._path}/{name}'):
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


def log_parameters(namespace: Handler, catalog: DataCatalog):
    # pylint: disable=protected-access
    namespace['parameters'] = catalog._data_sets['parameters'].load()


def log_dataset_metadata(namespace: Handler, name: str, dataset: AbstractDataSet):
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


def log_data_catalog_metadata(namespace: Handler, catalog: DataCatalog):
    # pylint: disable=protected-access
    namespace = namespace['catalog']

    for name, dataset in catalog._data_sets.items():
        if dataset.exists() and not namespace.container.exists(join_paths(namespace._path, name)):
            if not isinstance(dataset, MemoryDataSet) and not isinstance(dataset, NeptuneRunDataSet):
                log_dataset_metadata(namespace=namespace['datasets'], name=name, dataset=dataset)

            if isinstance(dataset, NeptuneFileDataSet):
                log_file_dataset(namespace=namespace['files'], name=name, dataset=dataset)

    log_parameters(namespace=namespace, catalog=catalog)


def log_pipeline_metadata(namespace: Handler, pipeline: Pipeline):
    namespace['structure'].upload(File.from_content(
        json.dumps(
            json.loads(pipeline.to_json()),
            indent=4,
            sort_keys=True
        ),
        'json'
    ))


def log_run_params(namespace: Handler, run_params: Dict[str, Any]):
    namespace['run_params'] = run_params


def log_command(namespace: Handler):
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
            save_version: str,
    ) -> None:
        self._run_id = hashlib.md5(save_version.encode()).hexdigest()
        os.environ['NEPTUNE_CUSTOM_RUN_ID'] = self._run_id

        catalog.add(
            data_set_name='neptune_run',
            data_set=NeptuneRunDataSet()
        )

    @hook_impl
    def before_pipeline_run(
            self,
            run_params: Dict[str, Any],
            pipeline: Pipeline,
            catalog: DataCatalog
    ) -> None:
        config = get_neptune_config(settings)

        run = neptune.init(api_token=config.api_token,
                           project=config.project,
                           mode=_connection_mode(config.enabled),
                           custom_run_id=self._run_id,
                           source_files=config.source_files or None)

        run[INTEGRATION_VERSION_KEY] = __version__

        current_namespace = run[config.base_namespace]

        os.environ['NEPTUNE_API_TOKEN'] = config.api_token or ''
        os.environ['NEPTUNE_PROJECT'] = config.project or ''

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
        run = catalog.load('neptune_run')
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

        run = catalog.load('neptune_run')
        current_namespace = run[f'nodes/{node.short_name}']
        current_namespace['execution_time'] = execution_time

        if outputs:
            current_namespace['outputs'] = list(sorted(outputs.keys()))

        log_data_catalog_metadata(namespace=run, catalog=catalog)
        run.container.sync()

    @hook_impl
    def after_pipeline_run(
            self,
            catalog: DataCatalog
    ) -> None:
        # pylint: disable=protected-access
        run = catalog.load('neptune_run')
        log_data_catalog_metadata(namespace=run, catalog=catalog)
        run.container.sync()


neptune_hooks = NeptuneHooks()
