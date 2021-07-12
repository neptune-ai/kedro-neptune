import os
import uuid
from pathlib import Path
from typing import Dict, Any

from kedro.pipeline import Pipeline
from kedro.io import DataCatalog
from kedro.framework.hooks import hook_impl
from kedro.framework.session import KedroSession


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
        metadata = _get_project_metadata(project_path=Path().cwd())
        session = KedroSession.create(metadata.package_name)
        context = session.load_context()
        credentials = context.config_loader.get("credentials*", "credentials*/**")

        os.environ.setdefault('NEPTUNE_API_TOKEN', credentials['neptune']['api_token'] or '')
        os.environ.setdefault('NEPTUNE_PROJECT', credentials['neptune']['api_token'] or '')
        os.environ.setdefault('NEPTUNE_CUSTOM_RUN_ID', repr(uuid.uuid4()))

        run = neptune.init()

        run[INTEGRATION_VERSION_KEY] = __version__


neptune_init = NeptuneInit()
