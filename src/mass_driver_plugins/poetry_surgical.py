"""Poetry package version bump"""

from copy import deepcopy

from mass_driver.drivers.bricks import SingleFileEditor
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from tree_sitter import Node, Parser
from tree_sitter_languages import get_language


class PoetrySurgical(SingleFileEditor):
    """Bump a package's major version in the pyproject.toml via Surgical editing

    Using the following:

    ```python
        Poetry(package="pytest", target="8.*", package_group="test")
    ```
    Will provide the following diff:

    ```diff
        [tool.poetry.group.test.dependencies]
        -pytest = "7.*"
        +pytest = "8.*"
    ```
    """

    language: str = "toml"

    target_file: str = "pyproject.toml"
    # DEBUG via website: https://tree-sitter.github.io/tree-sitter/playground
    query: str = """
    (table (dotted_key (dotted_key)) @k
        (pair) @p) @t
    """

    package: str
    """The target package to update major version for"""
    target: str
    """Major version to which to upgrade the package if possible"""
    package_group: str | None = None
    """Package group if any(as defined in poetry>1.2) where to find package"""

    @property
    def dependency_key(self) -> str:
        """Get the the dependencies key"""
        pkg_group = f".group.{self.package_group}" if self.package_group else ""
        return f"tool.poetry{pkg_group}.dependencies"

    def process_file(self, content_str: str) -> str | PatchResult:
        """Process the file"""
        language = get_language(self.language)
        query = language.query(self.query)
        parser = Parser()
        parser.set_language(language)
        tree = parser.parse(to_bytes(content_str))
        captures = query.captures(tree.root_node)
        dep_pairs = self.treesitter_query(captures, query, tree)
        if not dep_pairs:
            self.logger.error("No target found for replacement")
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details=f"Did not find the TOML section '{self.dependency_key}'",
            )
        to_replace_node = self.find_package(dep_pairs)
        if to_replace_node is None:
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details=f"Did not find package '{self.package}' in '{self.dependency_key}'",
            )
        edited_content = surgical_edit(content_str, self.target, to_replace_node)
        return edited_content

    def treesitter_query(self, captures, query, tree) -> list[Node]:
        """Search the tree for compatible node = pairs"""
        self.logger.info(f"Got {len(captures)} raw captures")
        # First grab all the surrounding table offsets
        table_ranges_set = set(
            [(n.start_point, n.end_point) for n, name in captures if name == "t"]
        )
        # And then query in depth for each of the tables one by one, scoped
        # Look for the k where it matches
        dep_pairs = []
        for tbl_start, tbl_end in sorted(list(table_ranges_set)):
            scoped_captures = query.captures(
                tree.root_node,
                start_point=tbl_start,
                end_point=tbl_end,
            )
            k_set = set([n.text for n, v in scoped_captures if v == "k"])
            k = k_set.pop()
            if k != to_bytes(self.dependency_key):
                continue  # Not the proper key
            dep_pairs = [n for n, v in scoped_captures if v == "p"]
            self.logger.info(
                f"Found key for table at range [{tbl_start[0]},{tbl_end[0]}], key='{k}', pairs: {[i.text for i in dep_pairs]}"
            )
            break  # This is the right pair, stop looking
        return dep_pairs

    def find_package(self, deps: list[Node]) -> Node | None:
        """Find the target package node, given all dep pairs"""
        target = None
        for node in deps:
            # In simple cases, we have the toml of:
            # package_name = '1.2.3'     equivalent to:
            # n.children[0] = n.children[2]
            pkg_node = node.children[0]
            if pkg_node.text != to_bytes(self.package):
                continue
            target = node.children[2]
            self.logger.info(f"Found dep {self.package}, with value {target.text}")
        return target


def surgical_edit(text, replacement, bad_node: Node) -> str:
    """Surgically edit the file to fix the badness

    In this case, we build a mutated line by using just the value we want,
    interpolated around the rest of the line.

    Particular attention is given to both beginning and end of original
    line, which could be housing some comments, which we don't want to edit.
    """
    mutated_lines = deepcopy(text).splitlines()
    # Visualisation of old content:
    #      stuff: value
    #             ^   ^
    #             b0  b1   [b0, b1] is bad_node start/end line/column
    b0_line, b0_col = bad_node.start_point
    b1_line, b1_col = bad_node.end_point
    bad_line = mutated_lines[b0_line]
    # New value
    #    key: REPLACEMENT
    #         ^          ^
    # up to b0[          [b1 onwards
    replaced_line = bad_line[:b0_col] + f'"{replacement}"' + bad_line[b1_col:]
    mutated_lines[b0_line] = replaced_line
    return "\n".join(mutated_lines) + "\n"


def to_bytes(content: str):
    """Dump content string to bytes via utf-8"""
    return bytes(content, encoding="utf-8")
