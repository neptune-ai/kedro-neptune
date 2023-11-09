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
__all__ = ["assert_structure"]

import hashlib
import os
import time
from ast import literal_eval
from typing import (
    List,
    Optional,
)

try:
    from neptune import (
        Run,
        init_run,
    )
except ImportError:
    from neptune.new import init_run
    from neptune.new.metadata_containers import Run


# It may take some time to refresh cache
# @backoff.on_exception(backoff.expo, AssertionError, max_value=1, max_time=60)
def assert_structure(travel_speed: int = 10000):
    time.sleep(30)
    with restore_run() as run:
        run.sync(wait=True)
        # Base run information
        assert run.exists("kedro")
        assert run.exists("kedro/catalog")
        assert run.exists("kedro/nodes")
        assert run.exists("kedro/kedro_command")
        assert run.exists("kedro/run_params")
        assert run.exists("kedro/structure")

        # Data catalog
        assert run.exists("kedro/catalog/datasets")
        assert run.exists("kedro/catalog/files")
        assert run.exists("kedro/catalog/parameters")

        assert run.exists("kedro/catalog/datasets/planets")

        assert run["kedro/catalog/datasets/planets"].fetch() == {
            "filepath": f"{os.getcwd()}/data/planets/planets.csv",
            "name": "planets",
            "protocol": "file",
            "save_args": {"index": False},
            "type": "CSVDataset",
            "version": "None",
        }

        assert run.exists("kedro/catalog/datasets/planets@neptune")
        assert run["kedro/catalog/datasets/planets@neptune"].fetch() == {
            "extension": "csv",
            "filepath": f"{os.getcwd()}/data/planets/planets.csv",
            "name": "planets@neptune",
            "protocol": "file",
            "type": "NeptuneFileDataSet",
            "version": "None",
        }
        assert run.exists("kedro/catalog/files/planets@neptune")
        run["kedro/catalog/files/planets@neptune"].download("/tmp/file")
        with open("/tmp/file", "rb") as handler:
            file_content = handler.read()
        assert hashlib.md5(file_content).hexdigest() == "af37712c8c80afc9690e4b70b7a590c5"

        assert run.exists("kedro/catalog/files/logo")
        run["kedro/catalog/files/logo"].download("/tmp/file")
        with open("/tmp/file", "rb") as handler:
            file_content = handler.read()
        assert hashlib.md5(file_content).hexdigest() == "85d289d3ed3f321557b6c428b7b35a67"

        assert run.exists("kedro/catalog/parameters/travel_speed")
        assert run["kedro/catalog/parameters/travel_speed"].fetch() == travel_speed

        # Nodes data
        check_node_metadata(
            run=run, node_namespace="kedro/nodes/distances", inputs=["planets"], outputs=["distances_to_planets"]
        )
        check_node_metadata(
            run=run,
            node_namespace="kedro/nodes/furthest",
            inputs=["distances_to_planets"],
            outputs=["furthest_planet_distance", "furthest_planet_name"],
        )
        check_node_metadata(run=run, node_namespace="kedro/nodes/judge_model", inputs=["neptune_run", "dataset"])
        check_node_metadata(
            run=run, node_namespace="kedro/nodes/prepare_dataset", inputs=["planets"], outputs=["dataset"]
        )
        check_node_metadata(
            run=run,
            node_namespace="kedro/nodes/travel_time",
            inputs=["furthest_planet_distance", "furthest_planet_name", "params:travel_speed"],
            outputs=["travel_hours"],
        )
        assert run.exists("kedro/nodes/travel_time/parameters")
        assert run.exists("kedro/nodes/travel_time/parameters/travel_speed")
        assert run["kedro/nodes/travel_time/parameters/travel_speed"].fetch() == travel_speed

        # User defined data
        assert run.exists("furthest_planet")
        assert run.exists("furthest_planet/name")
        assert run.exists("furthest_planet/travel_days")
        assert run.exists("furthest_planet/travel_hours")
        assert run.exists("furthest_planet/travel_months")
        assert run.exists("furthest_planet/travel_years")
        assert run["furthest_planet/name"].fetch() == "NEPTUNE"


def restore_run():
    return init_run(
        capture_stderr=False,
        capture_stdout=False,
        capture_hardware_metrics=False,
        capture_traceback=False,
        source_files=[],
    )


def check_node_metadata(run: Run, node_namespace: str, inputs: List, outputs: Optional[List] = None):
    assert run.exists(node_namespace)
    assert run.exists(f"{node_namespace}/execution_time")
    assert run.exists(f"{node_namespace}/inputs")
    assert sorted(literal_eval(run[f"{node_namespace}/inputs"].fetch())) == sorted(inputs)

    if outputs:
        assert run.exists(f"{node_namespace}/outputs")
        assert sorted(literal_eval(run[f"{node_namespace}/outputs"].fetch())) == sorted(outputs)
