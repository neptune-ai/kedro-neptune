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
# import hashlib
import os

from kedro.runner import ParallelRunner
from neptune import new as neptune

from tests.conftest import (  # check_node_metadata,
    prepare_testing_job,
    run_pipeline,
)

EXPECTED_SYNC_TIME = 0


class PlanetsTesting:
    def _test_planets_structure(self, run: neptune.Run, travel_speed: int = 10000):
        assert run.exists("kedro")
        assert run.exists("kedro/catalog")
        assert run.exists("kedro/nodes")
        assert run.exists("kedro/kedro_command")
        assert run.exists("kedro/run_params")
        assert run.exists("kedro/structure")

        assert run.exists("kedro/catalog/datasets")
        assert run.exists("kedro/catalog/files")
        assert run.exists("kedro/catalog/parameters")

        assert run.exists("kedro/catalog/datasets/planets")
        assert run["kedro/catalog/datasets/planets"].fetch() == {
            "filepath": f"{os.getcwd()}/data/planets/planets.csv",
            "name": "planets",
            "protocol": "file",
            "save_args": {"index": False},
            "type": "CSVDataSet",
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

        # assert run.exists("kedro/catalog/files/planets@neptune")
        # run["kedro/catalog/files/planets@neptune"].download("/tmp/file")
        # with open("/tmp/file", "rb") as handler:
        #     file_content = handler.read()
        # assert hashlib.md5(file_content).hexdigest() == "af37712c8c80afc9690e4b70b7a590c5"
        #
        # assert run.exists("kedro/catalog/files/logo")
        # run["kedro/catalog/files/logo"].download("/tmp/file")
        # with open("/tmp/file", "rb") as handler:
        #     file_content = handler.read()
        # assert hashlib.md5(file_content).hexdigest() == "85d289d3ed3f321557b6c428b7b35a67"
        #
        # assert run.exists("kedro/catalog/parameters/travel_speed")
        # assert run["kedro/catalog/parameters/travel_speed"].fetch() == travel_speed
        #
        # check_node_metadata(run, "kedro/nodes/distances", ["planets"], ["distances_to_planets"])
        #
        # check_node_metadata(
        #     run, "kedro/nodes/furthest",
        #     ["distances_to_planets"], ["furthest_planet_distance", "furthest_planet_name"]
        # )
        #
        # check_node_metadata(run, "kedro/nodes/judge_model", ["neptune_run", "dataset"])
        #
        # check_node_metadata(run, "kedro/nodes/prepare_dataset", ["planets"], ["dataset"])
        #
        # check_node_metadata(
        #     run,
        #     "kedro/nodes/travel_time",
        #     ["furthest_planet_distance", "furthest_planet_name", "params:travel_speed"],
        #     ["travel_hours"],
        # )
        # assert run.exists("kedro/nodes/travel_time/parameters")
        # assert run.exists("kedro/nodes/travel_time/parameters/travel_speed")
        # assert run["kedro/nodes/travel_time/parameters/travel_speed"].fetch() == travel_speed
        #
        # assert run.exists("furthest_planet")
        # assert run.exists("furthest_planet/name")
        # assert run.exists("furthest_planet/travel_days")
        # assert run.exists("furthest_planet/travel_hours")
        # assert run.exists("furthest_planet/travel_months")
        # assert run.exists("furthest_planet/travel_years")
        # assert run["furthest_planet/name"].fetch() == "NEPTUNE"


class TestPlanetsParallel(PlanetsTesting):
    def test_parallel(self):
        run_pipeline(project="planets", run_params={"runner": ParallelRunner(2)}, session_params={})
        run = prepare_testing_job()
        self._test_planets_structure(run)


# class TestPlanetsSequential(PlanetsTesting):
#     def test_sequential(self):
#         run_pipeline(project="planets", run_params={}, session_params={})
#         run = prepare_testing_job()
#         self._test_planets_structure(run)
#
#
# class TestPlanetsParameters(PlanetsTesting):
#     def test_parameters(self):
#         run_pipeline(project="planets", run_params={}, session_params={"extra_params": {"travel_speed": 40000}})
#         run = prepare_testing_job()
#         self._test_planets_structure(run, travel_speed=40000)
