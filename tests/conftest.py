from kedro.framework.session import KedroSession
import hashlib
import os
from typing import Dict, Any, Optional, List

try:
    # neptune-client=0.9.0 package structure
    from neptune import new as neptune
except ImportError:
    # neptune-client=1.0.0 package structure
    import neptune


def run_pipeline(project, project_path, run_params: Dict[str, Any] = {}, session_params: Dict[str, Any] = {}):
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
    assert run.exists(node_namespace)
    assert run.exists(f'{node_namespace}/execution_time')
    assert run.exists(f'{node_namespace}/inputs')
    assert sorted(eval(run[f'{node_namespace}/inputs'].fetch())) == inputs

    if outputs:
        assert run.exists(f'{node_namespace}/outputs')
        assert sorted(eval(run[f'{node_namespace}/outputs'].fetch())) == outputs