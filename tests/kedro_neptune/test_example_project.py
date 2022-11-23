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
# from kedro.runner import ParallelRunner

from tests.kedro_neptune.utils.kedro_utils import run_pipeline
from tests.kedro_neptune.utils.run_utils import assert_structure


def test_standard():
    run_pipeline(project="planets")
    assert_structure()


# def test_parallel_runner():
#     run_pipeline(project="planets", run_params={"runner": ParallelRunner(2)})
#     assert_structure()
#
#
# def test_run_with_params():
#     run_pipeline(project="planets", session_params={"extra_params": {"travel_speed": 40000}})
#     assert_structure(travel_speed=40000)
