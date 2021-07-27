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
from typing import Dict, Any, Optional, List

from kedro.framework.session import KedroSession


try:
    # neptune-client=0.9.0 package structure
    from neptune import new as neptune
except ImportError:
    # neptune-client=1.0.0 package structure
    import neptune


def run_pipeline(
        project: str,
        project_path: str,
        run_params: Dict[str, Any],
        session_params: Dict[str, Any]
):
    if 'NEPTUNE_CUSTOM_RUN_ID' in os.environ:
        del os.environ['NEPTUNE_CUSTOM_RUN_ID']

    with KedroSession.create(project, project_path, **session_params) as session:
        session.run(**run_params)

        run_id = session.store["session_id"]
        custom_run_id = hashlib.md5(run_id.encode()).hexdigest()

        return custom_run_id


def prepare_testing_job(custom_run_id):
    return neptune.init(
            project='common/kedro-integration',
            api_token='ANONYMOUS',
            custom_run_id=custom_run_id,
            capture_stderr=False,
            capture_stdout=False,
            capture_hardware_metrics=False,
            source_files=[]
        )


def check_dataset_metadata(run: neptune.Run, dataset_namespace: str):
    assert run.exists(f'{dataset_namespace}/filepath')
    assert run.exists(f'{dataset_namespace}/name')
    assert run.exists(f'{dataset_namespace}/protocol')
    assert run.exists(f'{dataset_namespace}/type')
    assert run.exists(f'{dataset_namespace}/version')


def check_node_metadata(run: neptune.Run, node_namespace: str, inputs: List, outputs: Optional[List] = None):
    # pylint: disable=eval-used
    assert run.exists(node_namespace)
    assert run.exists(f'{node_namespace}/execution_time')
    assert run.exists(f'{node_namespace}/inputs')
    assert sorted(eval(run[f'{node_namespace}/inputs'].fetch())) == inputs

    if outputs:
        assert run.exists(f'{node_namespace}/outputs')
        assert sorted(eval(run[f'{node_namespace}/outputs'].fetch())) == outputs
