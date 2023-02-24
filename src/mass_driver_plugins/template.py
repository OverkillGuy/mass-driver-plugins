"""Create templated files via Jinja2"""
from pathlib import Path
from typing import Any

from jinja2 import Environment
from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult


class TemplatedFile(PatchDriver):
    """Create a file via Jinja template filling"""

    target_file: str
    """The file to expand via template"""
    template: str
    """A jinja2 template"""
    context: dict[str, Any]
    """Per repo context for template expansion, with repo name as key"""
    jinja_args: dict
    """Extra args to give jinja templating"""

    def run(self, repo: Path) -> PatchResult:
        """Process the template file"""
        env = Environment(**self.jinja_args, autoescape=True)
        template = env.from_string(self.template)
        repo_name = repo.name
        context = self.context.get(repo_name)
        rendered = template.render(context)
        with open(repo / Path(self.target_file), "w") as fd:
            fd.write(rendered)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
