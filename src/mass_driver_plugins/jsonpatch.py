"""A JSON Patch (RFC6902) PatchDriver"""


import json
from pathlib import Path

import jsonpatch
from mass_driver.patchdriver import PatchDriver, PatchOutcome, PatchResult


class JsonPatch(PatchDriver):
    """Apply a JSON patch (RFC6902) on given file"""

    target_file: Path
    """File on which to apply Json Patch"""
    patch: list[dict] | str
    """JSON Patch, from RFC 6902"""

    def run(self, repo: Path) -> PatchResult:
        """Patch the given file"""
        breakpoint()
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
                json_dict = json.load(json_file)
        except Exception as e:
            return PatchResult(outcome=PatchOutcome.PATCH_ERROR, details=e)
        patched_json = jsonpatch.apply_patch(json_dict, patch)
        with open(json_filepath_abs, "w") as json_outfile:
            json.dump(patched_json, json_outfile)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
