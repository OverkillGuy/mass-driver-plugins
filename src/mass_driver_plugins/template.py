"""Create templated files via Jinja2"""

from jinja2 import Environment
from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class TemplatedFile(PatchDriver):
    """Create a file via Jinja template filling"""

    target_file: str
    """The file to expand via template"""
    template: str
    """A jinja2 template"""
    jinja_args: dict
    """Extra args to give jinja templating"""

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Process the template file"""
        env = Environment(**self.jinja_args, autoescape=True)
        template = env.from_string(self.template)
        rendered = template.render(repo.patch_data)
        with open(repo.cloned_path / self.target_file, "w") as fd:
            fd.write(rendered)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
