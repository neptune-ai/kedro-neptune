__all__ = ["__version__"]

import sys
from importlib.util import find_spec

if sys.version_info >= (3, 8):
    from importlib.metadata import (
        PackageNotFoundError,
        version,
    )
else:
    from importlib_metadata import (
        PackageNotFoundError,
        version,
    )

if not (find_spec("neptune") or find_spec("neptune-client")):
    msg = """
            The Neptune client library was not found.

            Install the neptune package with
                `pip install neptune`

            Need help? -> https://docs.neptune.ai/setup/installation/"""
    raise PackageNotFoundError(msg)

try:
    __version__ = version("kedro-neptune")
except PackageNotFoundError:
    # package is not installed
    pass
