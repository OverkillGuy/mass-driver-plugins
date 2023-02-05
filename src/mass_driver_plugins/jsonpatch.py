"""A JSON Patch (RFC6902) PatchDriver"""


import json
from pathlib import Path

import jsonpatch
import tomlkit
from mass_driver.patchdriver import PatchDriver, PatchOutcome, PatchResult
from ruamel import yaml


class JsonPatchBase(PatchDriver):
    """Base class for dict-based editing, regardless of type of file"""

    target_file: Path
    """File on which to apply Json Patch"""
    patch: list[dict] | str
    """JSON Patch, from RFC 6902"""

    def deserialize(self, file_contents: str) -> dict:
        """Load a data-tree particular file language of the day"""
        raise NotImplementedError("No serialize function implemented")

    def serialize(self, file_dict: dict) -> str:
        """Dump a data-tree back to string in the particular file language of the day"""
        raise NotImplementedError("No deserialize function implemented")

    def run(self, repo: Path) -> PatchResult:
        """Patch the given file"""
        patch = self.patch
        if isinstance(self.patch, list):
            patch = jsonpatch.JsonPatch(self.patch)
        json_filepath_abs = repo / self.target_file
        if not json_filepath_abs.is_file():
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details="No such file to patch",
            )
        try:
            with open(json_filepath_abs) as json_file:
                json_dict = self.deserialize(json_file.read())
        except Exception as e:
            return PatchResult(outcome=PatchOutcome.PATCH_ERROR, details=e)
        patched_json = jsonpatch.apply_patch(json_dict, patch)
        with open(json_filepath_abs, "w") as json_outfile:
            json_outfile.write(self.serialize(patched_json))
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)


class JsonPatch(JsonPatchBase):
    """Apply a JSON patch (RFC6902) on given JSON file"""

    def deserialize(self, file_contents: str) -> dict:
        """Load a data-tree particular file language of the day"""
        return json.loads(file_contents)

    def serialize(self, file_dict: dict) -> str:
        """Dump a data-tree back to string in the particular file language of the day"""
        return json.dumps(file_dict)


class YamlPatch(JsonPatchBase):
    """Apply a JSON patch (RFC6902) on given YAML file"""

    def deserialize(self, file_contents: str) -> dict:
        """Load a data-tree particular file language of the day"""
        return yaml.load(file_contents)

    def serialize(self, file_dict: dict) -> str:
        """Dump a data-tree back to string in the particular file language of the day"""
        return yaml.dump(file_dict)


class TomlPatch(JsonPatchBase):
    """Apply a JSON patch (RFC6902) on given TOML file"""

    def deserialize(self, file_contents: str) -> dict:
        """Load a data-tree particular file language of the day"""
        return tomlkit.loads(file_contents)

    def serialize(self, file_dict: dict) -> str:
        """Dump a data-tree back to string in the particular file language of the day"""
        return tomlkit.dumps(file_dict)
