"""Test all the drivers we package"""

from pathlib import Path

import pytest
from mass_driver.tests.fixtures import copy_folder, massdrive_check_file

# Go from this filename.py to folder:
# ./test_drivers.py -> ./test_drivers/
TESTS_FOLDER = Path(__file__).with_suffix("")


@pytest.mark.parametrize(
    "test_folder", [f.name for f in TESTS_FOLDER.iterdir() if f.is_dir()]
)
def test_driver_one(test_folder: Path, tmp_path, monkeypatch):
    """Check a single pattern"""
    absolute_reference = TESTS_FOLDER / test_folder
    workdir = tmp_path / "repo"
    copy_folder(absolute_reference, workdir)
    monkeypatch.chdir(workdir)
    massdrive_check_file(workdir)
