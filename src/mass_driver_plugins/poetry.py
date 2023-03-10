"""Poetry package version bump"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from jsonpointer import resolve_pointer, set_pointer
from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from poetry.core.pyproject.toml import PyProjectTOML


def get_pyproject(repo_path: Path):
    """Grab the pyproject object"""
    return PyProjectTOML(repo_path / "pyproject.toml")


@dataclass
class Poetry(PatchDriver):
    """Bump a package's major version in the pyproject.toml

    Using the following:

    .. code:: python

        Poetry(package="pytest",target_major="8",package_group="test")

    Will provide the following diff:

    .. code-block:: diff

        [tool.poetry.group.test.dependencies]
        -pytest = "7.*"
        +pytest = "8.*"
    """

    package: str
    """The target package to update major version for"""
    target_major: str
    """Major version to which to upgrade the package if possible"""
    package_group: Optional[str] = None
    """Package group if any(as defined in poetry>1.2) where to find package"""

    @property
    def json_pointer(self):
        """Get the JSON Pointer (RFC6901) for the package we're looking for"""
        if self.package_group:
            return (
                f"/tool/poetry/group/{self.package_group}/dependencies/{self.package}"
            )
        else:
            return f"/tool/poetry/dependencies/{self.package}"

    def run(self, repo: Path) -> PatchResult:
        """Process the major bump file"""
        project = get_pyproject(repo)
        dep_version = resolve_pointer(project.data, self.json_pointer, None)
        if not dep_version:
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details=f"Didn't find {self.package} in pyproject.toml test deps!",
            )
        major_version, *other_versions = dep_version.split(".")
        inferior_version = int(major_version) < int(self.target_major)
        if not inferior_version:
            return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
        set_pointer(project.data, self.json_pointer, f"{self.target_major}.*")
        project.save()
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
