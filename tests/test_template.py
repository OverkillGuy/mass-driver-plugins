"""Validate the template"""

from pathlib import Path

# from mass_driver.migration import Migration
from mass_driver.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import copy_folder, massdrive

CONFIG_FILENAME = "template_migration.toml"


def test_template_expansion(tmp_path, datadir):
    """Scenario: Use the template expander PatchDriver"""
    # Given a sample repo to mass-drive
    # And sample repo has counter at value 1
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(datadir / "sample_repo"), repo_path)
    config_filepath = datadir / CONFIG_FILENAME
    # migration = Migration.from_config(config_filepath.read_text())
    # When I run mass-driver
    result = massdrive(
        repo_path,
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
