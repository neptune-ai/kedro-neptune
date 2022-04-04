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
import hashlib
import time
from ast import literal_eval
from typing import Dict, Any, Optional, List

from kedro.framework.project import configure_project
from kedro.framework.session import KedroSession


try:
    # neptune-client=0.9.0 package structure
    from neptune import new as neptune
except ImportError:
    # neptune-client=1.0.0 package structure
    import neptune


def run_pipeline(
        project: str,
        run_params: Dict[str, Any],
        session_params: Dict[str, Any]
):
    if 'NEPTUNE_CUSTOM_RUN_ID' in os.environ:
        del os.environ['NEPTUNE_CUSTOM_RUN_ID']

    configure_project(project)
    with KedroSession.create(project, **session_params) as session:
        session.run(**run_params)

        run_id = session.store["session_id"]
        custom_run_id = hashlib.md5(run_id.encode()).hexdigest()

    # wait for the queues to finish syncing data to server
    time.sleep(5)
    return custom_run_id


def prepare_testing_job(custom_run_id):
    return neptune.init(
        custom_run_id=custom_run_id,
        capture_stderr=False,
        capture_stdout=False,
        capture_hardware_metrics=False,
        capture_traceback=False,
        source_files=[]
    )


def check_node_metadata(run: neptune.Run, node_namespace: str, inputs: List, outputs: Optional[List] = None):
    assert run.exists(node_namespace)
    assert run.exists(f'{node_namespace}/execution_time')
    assert run.exists(f'{node_namespace}/inputs')
    assert sorted(literal_eval(run[f'{node_namespace}/inputs'].fetch())) == inputs

    if outputs:
        assert run.exists(f'{node_namespace}/outputs')
        assert sorted(literal_eval(run[f'{node_namespace}/outputs'].fetch())) == outputs
