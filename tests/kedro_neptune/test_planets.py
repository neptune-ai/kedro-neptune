import hashlib
import os
import time
from kedro.runner import ParallelRunner

from neptune import new as neptune

from tests.conftest import (
    run_pipeline,
    prepare_testing_job,
    check_dataset_metadata,
    check_node_metadata
)

EXPECTED_SYNC_TIME = 240


class TestPlanets:
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
        check_dataset_metadata(run, 'kedro/catalog/datasets/planets')

        assert run.exists('kedro/catalog/datasets/planets@neptune')
        check_dataset_metadata(run, 'kedro/catalog/datasets/planets@neptune')

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

        check_node_metadata(run, 'kedro/nodes/optimize', ['model', 'neptune_metadata'])

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

    # def test_sequential(self):
    #     custom_run_id = run_pipeline(project="planets", project_path="examples/planets")
    #     time.sleep(EXPECTED_SYNC_TIME)
    #     run = prepare_testing_job(custom_run_id)
    #     self._test_planets_structure(run)
    #
    # def test_parameters(self):
    #     custom_run_id = run_pipeline(
    #         project="planets",
    #         project_path="examples/planets",
    #         session_params={
    #             'extra_params': {
    #                 'travel_speed': 40000
    #             }
    #         }
    #     )
    #     time.sleep(EXPECTED_SYNC_TIME)
    #     run = prepare_testing_job(custom_run_id)
    #     self._test_planets_structure(run, travel_speed=40000)

    def test_parallel(self):
        custom_run_id = run_pipeline(
            project="planets",
            project_path="examples/planets",
            run_params={
                'runner': ParallelRunner(1)
            }
        )
        time.sleep(EXPECTED_SYNC_TIME)
        run = prepare_testing_job(custom_run_id)
        self._test_planets_structure(run)
