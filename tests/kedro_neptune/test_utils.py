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
from unittest import mock
from unittest.mock import patch

from kedro_neptune.utils import (
    ensure_bool,
    get_kedro_env,
)


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


class TestGetKedroEnv:
    def _test_get_kedro_env(self, config_loader_args: dict, expected: str) -> None:
        settings = mock.Mock()
        settings.CONFIG_LOADER_ARGS = config_loader_args
        assert get_kedro_env(settings) == expected

    def test_env_from_commandline(self):
        """Test that the function returns the value of the `--env` commandline argument."""
        with patch("sys.argv", ["kedro", "run", "--env", "test"]):
            self._test_get_kedro_env(config_loader_args={}, expected="test")

    def test_env_from_environment_variable(self):
        """Test that the function returns the value of the `$KEDRO_ENV` environment variable."""
        with patch("os.environ", {"KEDRO_ENV": "test"}):
            self._test_get_kedro_env(config_loader_args={}, expected="test")

    def test_env_from_default_run_env(self):
        """Test that the function returns the value of `settings.CONFIG_LOADER_ARGS["default_run_env"]`."""
        self._test_get_kedro_env(config_loader_args={"default_run_env": "test"}, expected="test")

    def test_env_from_base_env(self):
        """Test that the function returns the value of `settings.CONFIG_LOADER_ARGS["base_env"]`."""
        self._test_get_kedro_env(config_loader_args={"base_env": "test"}, expected="test")

    def test_env_none(self):
        """Test that the function returns `None` when none of the above conditions are met."""
        self._test_get_kedro_env(config_loader_args={}, expected=None)

    def test_order_of_precedence(self):
        """Test that the environment is read from `sys.argv`, `$KEDRO_ENV`,
        `settings.CONFIG_LOADER_ARGS["default_run_env"]` or `settings.CONFIG_LOADER_ARGS["base_env"]`,
        in order of precedence"""

        with patch("sys.argv", ["kedro", "run", "--env", "argv"]), patch("os.environ", {"KEDRO_ENV": "env"}):
            self._test_get_kedro_env(
                config_loader_args={"default_run_env": "default", "base_env": "base"},
                expected="argv",
            )
