#
# Copyright (c) 2022, Neptune Labs Sp. z o.o.
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
    "ensure_bool",
    "parse_config_value",
    "get_kedro_env",
]

import os
import sys
from typing import (
    Any,
    Optional,
    Union,
)


def parse_config_value(config_value: Any):
    return extract_env_variable(value=config_value)


def extract_env_variable(value: Any):
    if isinstance(value, str) and value.startswith("$"):
        return os.environ.get(value[1:], "")
    return value


def ensure_bool(value: Optional[Union[str, bool]]) -> bool:
    if isinstance(value, str):
        return value.lower().strip() not in ("false", "no", "0")

    return value


def get_kedro_env(settings: object) -> Optional[str]:
    """Returns kedro configuration environment to use.

    Args:
        settings (object): Kedro settings.

    Returns:
        Optional[str]: `--env` commandline argument's value,
            `$KEDRO_ENV` value, `settings.CONFIG_LOADER_ARGS["default_run_env"]`
            or `settings.CONFIG_LOADER_ARGS["base_env"]`.
    """
    for i, arg in enumerate(sys.argv):
        if arg == "--env" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return (
        os.getenv("KEDRO_ENV")
        or settings.CONFIG_LOADER_ARGS.get("default_run_env")
        or settings.CONFIG_LOADER_ARGS.get("base_env")
    )
