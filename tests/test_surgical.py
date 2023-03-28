"""Validate the template"""

import os
from pathlib import Path

from mass_driver.models.activity import load_activity_toml
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import copy_folder, massdrive

CONFIG_FILENAME = "surgical_migration.toml"


def test_surgical(tmp_path, datadir, mocker):
    """Scenario: Surgically editing Github Actions file"""
    # Given a sample repo to mass-drive
    # And sample repo with a github action file
    mocker.patch.dict(os.environ, {"FORGE_TOKEN": "ghp_supersecrettoken"})
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(datadir / "sample_repo"), repo_path)
    config_filepath = datadir / CONFIG_FILENAME
    migration = load_activity_toml(config_filepath.read_text()).migration
    # When I run mass-driver
    migration_result, _forge_result = massdrive(
        str(repo_path),
        config_filepath,
    )
    assert (
        migration_result.outcome == PatchOutcome.PATCHED_OK
    ), f"Wrong outcome from patching: {migration_result.details}"
    target_text_post = (repo_path / migration.driver_config["target_file"]).read_text()
    reference_text = (repo_path / "good.yaml").read_text()
    # Then the changed file is identical to a reference
    assert target_text_post == reference_text, "Post-change file should match reference"
