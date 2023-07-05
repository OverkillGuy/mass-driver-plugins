"""Validate the template"""

from pathlib import Path

# from mass_driver.migration import Migration
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import copy_folder, massdrive_runlocal, repoize

CONFIG_FILENAME = "template_migration.toml"


def test_template_expansion(tmp_path, datadir, monkeypatch):
    """Scenario: Use the template expander PatchDriver"""
    # Given a sample repo to mass-drive
    # And sample repo has counter at value 1
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(datadir / "sample_repo"), repo_path)
    repoize(repo_path)
    config_filepath = datadir / CONFIG_FILENAME
    monkeypatch.chdir(repo_path)
    # When I run mass-driver
    result = massdrive_runlocal(
        None,
        config_filepath,
    )
    migration_result = result.migration_result["test_repo"]
    assert (
        migration_result.outcome == PatchOutcome.PATCHED_OK
    ), f"Wrong outcome from patching: {migration_result.details}"
    # target_text_post = (repo_path / migration.driver.target_file).read_text()
    # # Then the counter is bumped to config value
    # # Note: Different configfilename set the target_count to different value
    # assert (
    #     int(counter_text_post) == migration.driver.target_count
    # ), "Counter not updated properly"
