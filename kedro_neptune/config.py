import os
from typing import List
from dataclasses import dataclass

from kedro.framework.session import KedroSession, get_current_session


def _parse_config_input(config_input):
    if config_input.startswith('$'):
        parsed_input = os.environ.get(config_input[1:])
    else:
        parsed_input = config_input
    return parsed_input


@dataclass()
class NeptuneConfig:
    api_token: str
    project: str
    base_namespace: str
    source_files: List[str]
    enabled: bool


def get_neptune_config() -> NeptuneConfig:
    session: KedroSession = get_current_session()
    context = session.load_context()
    # pylint: disable=protected-access
    credentials = context._get_config_credentials()
    config = context.config_loader.get('neptune**')

    api_token = _parse_config_input(credentials['neptune']['api_token'])
    project = _parse_config_input(config['neptune']['project'])
    base_namespace = config['neptune']['base_namespace']
    source_files = config['neptune']['upload_source_files']
    enabled = config['neptune'].get('enabled', True)

    return NeptuneConfig(
        api_token=api_token,
        project=project,
        base_namespace=base_namespace,
        source_files=source_files,
        enabled=enabled
    )
