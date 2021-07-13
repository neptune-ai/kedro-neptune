import os
import time
import hashlib
from typing import Dict, Any, Optional

from kedro.io import DataCatalog
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from kedro.framework.hooks import hook_impl
from kedro.framework.session import get_current_session


try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
    from neptune.new.internal.utils import verify_type
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune
    from neptune.internal.utils import verify_type


from kedro_neptune import __version__


INTEGRATION_VERSION_KEY = 'source_code/integrations/kedro-neptune'


class NeptuneInit:
    @hook_impl
    def before_pipeline_run(
            self,
            run_params: Dict[str, Any],
            pipeline: Pipeline,
            catalog: DataCatalog
    ) -> None:
        session = get_current_session()
        context = session.load_context()
        credentials = context._get_config_credentials()
        config = context.config_loader.get('neptune**')

        os.environ.setdefault('NEPTUNE_API_TOKEN', credentials['neptune']['NEPTUNE_API_TOKEN'] or '')
        os.environ.setdefault('NEPTUNE_PROJECT', config['neptune']['project'] or '')
        os.environ.setdefault('NEPTUNE_CUSTOM_RUN_ID', hashlib.md5(repr(time.time()).encode()).hexdigest())

        run = neptune.init(monitoring_namespace='monitoring')
        run[INTEGRATION_VERSION_KEY] = run_params.get('kedro_version', __version__)

    @hook_impl
    def before_node_run(
            self,
            node: Node,
            catalog: DataCatalog,
            inputs: Dict[str, Any],
            is_async: bool,
            run_id: str,
    ):
        os.environ['NEPTUNE_MONITORING_NAMESPACE'] = f'monitoring/{node.short_name}'


neptune_init = NeptuneInit()
