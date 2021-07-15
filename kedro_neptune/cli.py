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

import os
import yaml

import click

from kedro.framework.project import settings
from kedro.framework.session import KedroSession
from kedro.framework.startup import ProjectMetadata


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
@click.pass_obj
def init(metadata: ProjectMetadata, api_token: str, project: str, base_namespace: str):
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

    context.config_file = context.project_path / settings.CONF_ROOT / 'base' / "neptune.yml"

    if not context.config_file.exists():
        with context.config_file.open("w") as config_file:
            yaml.dump({
                'neptune': {
                    'base_namespace': base_namespace,
                    'project': project,
                    'upload_source_files': ['**/*.py',  'conf/base/*.yml']
                }
            }, config_file, default_flow_style=False)
