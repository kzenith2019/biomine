from pathlib import Path
import pytest

@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed").mkdir()
    (tmp_path / "features").mkdir()
    return tmp_path
