"""A JSON Patch (RFC6902) PatchDriver"""


import json

import jsonpatch
from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo
from pydantic import Extra, FilePath
from ruamel import yaml


class JsonPatchBase(PatchDriver):
    """Base class for dict-based editing, regardless of type of file"""

    target_file: FilePath
    """File on which to apply Json Patch"""
    patch: list[dict] | str
    """JSON Patch, from RFC 6902"""

    class Config:
        """Configuration of the JsonPatch class"""

        extra = Extra.allow

    def deserialize(self, fd) -> dict:
        """Load a data-tree particular file language of the day"""
        raise NotImplementedError("No serialize function implemented")

    def serialize(self, file_dict: dict, fd):
        """Dump a data-tree back to string in the particular file language of the day"""
        raise NotImplementedError("No deserialize function implemented")

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Patch the given file"""
        patch = self.patch
        if isinstance(self.patch, list):
            patch = jsonpatch.JsonPatch(self.patch)
        json_filepath_abs = repo.cloned_path / self.target_file
        if not json_filepath_abs.is_file():
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details="No such file to patch",
            )
        try:
            with open(json_filepath_abs, "rb") as json_file:
                json_dict = self.deserialize(json_file)
        except Exception as e:
            return PatchResult(outcome=PatchOutcome.PATCH_ERROR, details=str(e))
        patched_json = jsonpatch.apply_patch(json_dict, patch)
        with open(json_filepath_abs, "w") as json_outfile:
            self.serialize(patched_json, json_outfile)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)


class JsonPatch(JsonPatchBase):
    """Apply a JSON patch (RFC6902) on given JSON file"""

    def deserialize(self, fd) -> dict:
        """Load a data-tree particular file language of the day"""
        return json.load(fd)

    def serialize(self, file_dict: dict, fd):
        """Dump a data-tree back to string in the particular file language of the day"""
        json.dump(file_dict, fd)


class YamlPatch(JsonPatchBase):
    """Apply a JSON patch (RFC6902) on given YAML file"""

    def deserialize(self, fd):
        """Load a data-tree particular file language of the day"""
        self._yaml = yaml.YAML(typ="rt")
        self._yaml.indent(mapping=2, sequence=4, offset=2)
        return self._yaml.load(fd)

    def serialize(self, file_dict: dict, fd):
        """Dump a data-tree back to string in the particular file language of the day"""
        self._yaml.dump(file_dict, fd)
