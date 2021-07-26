import pytest

try:
    # neptune-client=0.9.0 package structure
    from neptune import new as neptune
except ImportError:
    # neptune-client=1.0.0 package structure
    import neptune


@pytest.fixture()
def dataset():
    pass
