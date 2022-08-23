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
from kedro_neptune.utils import ensure_bool


class TestUtils:
    def test_ensure_bool(self):
        assert ensure_bool(value=False) is False
        assert ensure_bool(value="FALSE") is False
        assert ensure_bool(value="  False ") is False
        assert ensure_bool(value="False") is False
        assert ensure_bool(value="false") is False
        assert ensure_bool(value="no") is False
        assert ensure_bool(value="0") is False

        assert ensure_bool(value=True) is True
        assert ensure_bool(value="") is True
        assert ensure_bool(value="non_boolean") is True
        assert ensure_bool(value="1") is True
        assert ensure_bool(value="TRUE") is True
        assert ensure_bool(value=" True  ") is True
        assert ensure_bool(value="True") is True
        assert ensure_bool(value="true") is True
