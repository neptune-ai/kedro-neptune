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
from dataclasses import dataclass
from typing import List

from kedro_neptune.utils import (
    ensure_bool,
    parse_config_value,
)


@dataclass()
class NeptuneConfig:
    api_token: str
    project: str
    base_namespace: str
    source_files: List[str]
    enabled: bool


def get_neptune_config(settings) -> NeptuneConfig:
    config_loader = settings.CONFIG_LOADER_CLASS(settings.CONF_SOURCE, **settings.CONFIG_LOADER_ARGS)
    credentials = config_loader["credentials_neptune"]
    config = config_loader["neptune"]

    api_token = parse_config_value(credentials["neptune"]["api_token"])
    project = parse_config_value(config["neptune"]["project"])
    base_namespace = parse_config_value(config["neptune"]["base_namespace"])
    source_files = parse_config_value(config["neptune"]["upload_source_files"])
    enabled = ensure_bool(parse_config_value(config["neptune"].get("enabled", True)))

    return NeptuneConfig(
        api_token=api_token, project=project, base_namespace=base_namespace, source_files=source_files, enabled=enabled
    )
