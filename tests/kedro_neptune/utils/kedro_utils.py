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
__all__ = ["run_pipeline"]

from pathlib import Path
from typing import (
    Any,
    Dict,
)

from kedro.framework.project import configure_project
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project


def run_pipeline(project: str, run_params: Dict[str, Any] = None, session_params: Dict[str, Any] = None):
    if run_params is None:
        run_params = {}

    if session_params is None:
        session_params = {}
    configure_project(project)

    bootstrap_project(Path(".").resolve())

    with KedroSession.create(**session_params) as session:
        session.run(**run_params)
