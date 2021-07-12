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

__all__ = [
    '__version__'
]


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new.internal.utils import verify_type
    from neptune.new.internal.utils.compatibility import expect_not_an_experiment
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.internal.utils import verify_type
    from neptune.internal.utils.compatibility import expect_not_an_experiment

INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'
