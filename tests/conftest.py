import pytest
import yaml
from pathlib import Path
from bilayers_schema import schema as _schema

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def schema():
    return _schema


@pytest.fixture
def classical_segmentation_config():
    with open(FIXTURES_DIR / "classical_segmentation.yaml") as f:
        return yaml.safe_load(f)
