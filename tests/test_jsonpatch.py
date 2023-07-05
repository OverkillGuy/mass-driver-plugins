"""Validate the template"""

from pathlib import Path

import pytest

# from mass_driver.migration import Migration
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import copy_folder, massdrive


@pytest.mark.parametrize(
    "config_filename",
    [
        "migration_json.toml",
        "migration_yaml.toml",
    ],
)
def test_template_expansion(tmp_path, datadir, config_filename, monkeypatch):
    """Scenario: Use the json/yaml/tomlpatcher PatchDriver"""
    # Given a sample repo to mass-drive
    # And sample repo has counter at value 1
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(datadir / "sample_repo"), repo_path)
    config_filepath = datadir / config_filename
    monkeypatch.chdir(repo_path)
    # migration = Migration.from_config(config_filepath.read_text())
    # When I run mass-driver
    result, _forge_junk, _scan_junk = massdrive(
        str(repo_path),
        config_filepath,
    )
    assert (
        result.outcome == PatchOutcome.PATCHED_OK
    ), f"Wrong outcome from patching: {result.details}"
    # target_text_post = (repo_path / migration.driver.target_file).read_text()
    # # Then the counter is bumped to config value
    # # Note: Different configfilename set the target_count to different value
    # assert (
    #     int(counter_text_post) == migration.driver.target_count
    # ), "Counter not updated properly"
