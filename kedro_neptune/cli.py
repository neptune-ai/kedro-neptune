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

import yaml

import click

from kedro.framework.project import settings
from kedro.framework.session import get_current_session


@click.group(name="Neptune")
def commands():
    """Kedro plugin for logging with Neptune.ai"""
    pass


@commands.group(name="neptune")
def neptune_commands():
    pass


CREDENTIALS_CONFIG = {
    'neptune': {
        'api_token': '',
        'project': ''
    }
}

INITIAL_PROJECT_SETTINGS = {
    'base_namesapce': 'kedro'
}


@neptune_commands.command()
def init():
    session = get_current_session()
    context = session.load_context()

    context.credentials_file = context.project_path / settings.CONF_ROOT / 'local' / "credentials_neptune.yml"

    if not context.credentials_file.exists():
        with context.credentials_file.open("w") as config_file:
            yaml.dump(CREDENTIALS_CONFIG, config_file, default_flow_style=False)

    context.config_file = context.project_path / settings.CONF_ROOT / 'base' / "neptune.yml"

    if not context.config_file.exists():
        with context.config_file.open("w") as config_file:
            yaml.dump(INITIAL_PROJECT_SETTINGS, config_file, default_flow_style=False)
