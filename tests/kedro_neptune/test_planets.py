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
from kedro.runner import ParallelRunner

from neptune import new as neptune

from tests.conftest import (
    run_pipeline,
    prepare_testing_job,
    check_node_metadata
)

EXPECTED_SYNC_TIME = 0


class PlanetsTesting:
    def _test_planets_structure(self, run: neptune.Run, travel_speed: int = 10000):
        assert run.exists('sys')
        assert run.exists('kedro')
        assert run.exists('monitoring')
        assert run.exists('source_code')

        assert run.exists('kedro/catalog')
        assert run.exists('kedro/nodes')
        assert run.exists('kedro/kedro_command')
        assert run.exists('kedro/run_params')
        assert run.exists('kedro/structure')

        assert run.exists('kedro/catalog/datasets')
        assert run.exists('kedro/catalog/files')
        assert run.exists('kedro/catalog/parameters')

        assert run.exists('kedro/catalog/datasets/planets')
        assert run['kedro/catalog/datasets/planets'].fetch() == {
            'filepath': f'{os.getcwd()}/data/planets/planets.csv',
            'name': 'planets',
            'protocol': 'file',
            'save_args': {'index': False},
            'type': 'CSVDataSet',
            'version': 'None'
        }

        assert run.exists('kedro/catalog/datasets/planets@neptune')
        assert run['kedro/catalog/datasets/planets@neptune'].fetch() == {
            'extension': 'csv',
            'filepath': f'{os.getcwd()}/data/planets/planets.csv',
            'name': 'planets@neptune',
            'protocol': 'file',
            'type': 'NeptuneFileDataSet',
            'version': 'None'
        }

        assert run.exists('kedro/catalog/files/planets@neptune')
        run['kedro/catalog/files/planets@neptune'].download('/tmp/file')
        with open('/tmp/file', 'rb') as handler:
            file_content = handler.read()
        assert hashlib.md5(file_content).hexdigest() == 'af37712c8c80afc9690e4b70b7a590c5'

        assert run.exists('kedro/catalog/files/last_model')

        assert run.exists('kedro/catalog/files/logo')
        run['kedro/catalog/files/logo'].download('/tmp/file')
        with open('/tmp/file', 'rb') as handler:
            file_content = handler.read()
        assert hashlib.md5(file_content).hexdigest() == '85d289d3ed3f321557b6c428b7b35a67'

        assert run.exists('kedro/catalog/parameters/travel_speed')
        assert run['kedro/catalog/parameters/travel_speed'].fetch() == travel_speed

        check_node_metadata(
            run,
            'kedro/nodes/distances',
            ['planets'],
            ['distances_to_planets']
        )

        check_node_metadata(
            run,
            'kedro/nodes/furthest',
            ['distances_to_planets'],
            ['furthest_planet_distance', 'furthest_planet_name']
        )

        check_node_metadata(run, 'kedro/nodes/optimize', ['model', 'neptune_run'])

        check_node_metadata(run, 'kedro/nodes/prepare_dataset', ['planets'], ['dataset'])

        check_node_metadata(run, 'kedro/nodes/prepare_model', ['dataset'], ['model'])

        check_node_metadata(
            run,
            'kedro/nodes/travel_time',
            ['furthest_planet_distance', 'furthest_planet_name', 'params:travel_speed'],
            ['travel_hours']
        )
        assert run.exists('kedro/nodes/travel_time/parameters')
        assert run.exists('kedro/nodes/travel_time/parameters/travel_speed')
        assert run['kedro/nodes/travel_time/parameters/travel_speed'].fetch() == travel_speed

        assert run.exists('furthest_planet')
        assert run.exists('furthest_planet/name')
        assert run.exists('furthest_planet/travel_days')
        assert run.exists('furthest_planet/travel_hours')
        assert run.exists('furthest_planet/travel_months')
        assert run.exists('furthest_planet/travel_years')
        assert run['furthest_planet/name'].fetch() == 'NEPTUNE'

        assert run.exists('kedro/moons_classifier/best')
        assert run.exists('kedro/moons_classifier/study')
        assert run.exists('kedro/moons_classifier/trials')
        assert run.exists('kedro/moons_classifier/visualizations')

        assert run.exists('kedro/moons_classifier/trials/trials')
        assert run.exists('kedro/moons_classifier/trials/trials/0')
        assert run.exists('kedro/moons_classifier/trials/trials/1')
        assert run.exists('kedro/moons_classifier/trials/trials/2')
        assert run.exists('kedro/moons_classifier/trials/trials/3')
        assert run.exists('kedro/moons_classifier/trials/trials/4')
        assert run.exists('kedro/moons_classifier/trials/trials/0/metrics')
        assert run.exists('kedro/moons_classifier/trials/trials/0/io_files')
        assert run.exists('kedro/moons_classifier/trials/trials/0/config')


class TestPlanetsParallel(PlanetsTesting):
    def test_parallel(self):
        custom_run_id = run_pipeline(
            project="planets",
            run_params={
                'runner': ParallelRunner(2)
            },
            session_params={}
        )
        run = prepare_testing_job(custom_run_id)
        self._test_planets_structure(run)


class TestPlanetsSequential(PlanetsTesting):
    def test_sequential(self):
        custom_run_id = run_pipeline(
            project="planets",
            run_params={},
            session_params={}
        )
        run = prepare_testing_job(custom_run_id)
        self._test_planets_structure(run)


class TestPlanetsParameters(PlanetsTesting):
    def test_parameters(self):
        custom_run_id = run_pipeline(
            project="planets",
            run_params={},
            session_params={
                'extra_params': {
                    'travel_speed': 40000
                }
            }
        )
        run = prepare_testing_job(custom_run_id)
        self._test_planets_structure(
            run,
            travel_speed=40000
        )
