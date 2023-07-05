"""Edit files via tree-sitter"""
from copy import deepcopy
from pathlib import Path
from typing import Any

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo
from tree_sitter import Node, Parser
from tree_sitter_languages import get_language


class SurgicalFileEditor(PatchDriver):
    """
    Edit files surgically, parsing them with tree-sitter

    Uses tree-sitter to parse a file, then tree-sitter query pre-selects nodes,
    a selection refinement function narrows down nodes to change, and a surgical
    editing function tweaks the file content to "fix" it.

    Due to tree-sitter queries being under-expressive, the class config isn't
    enough to customize the class for reusability without Python code changes.
    Thus this class is just the skeleton, with some functions intentionally not
    implemented, to be overriden by downstream.
    """

    target_file: str
    """The file to read"""
    language: str
    """The tree-sitter grammar to use"""
    query: str
    """The tree-sitter query to process"""

    def treesitter_query(self, captures) -> list[Node]:
        """Search the tree for compatible nodes"""
        raise NotImplementedError(
            "Base class doesn't know to process tree-sitter queries"
        )

    def refine_search(self, matching_nodes) -> list[Any]:
        """Refine keyword matches"""
        raise NotImplementedError("Base class doesn't know to refine node search")

    def surgical_edit(self, text, bad_nodes: list[Any]) -> str:
        """Surgically edit the file to fix the badness"""
        raise NotImplementedError("Base class doesn't know to surgically edit the file")

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Process the template file"""
        target_fullpath = repo.cloned_path / Path(self.target_file)
        content_str = target_fullpath.read_text()
        language = get_language(self.language)
        query = language.query(self.query)
        parser = Parser()
        parser.set_language(language)
        tree = parser.parse(bytes(content_str, "utf8"))
        captures = query.captures(tree.root_node)
        prematching = self.treesitter_query(captures)
        bad_nodes = self.refine_search(prematching)
        mutated_content = self.surgical_edit(content_str, bad_nodes)
        target_fullpath.write_text(mutated_content)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)


class GithubActionParameterReplacer(SurgicalFileEditor):
    """Replaces a Github action's parameter

    Assumes a YAML file is fed in target_file, for which the Github Actions
    structure will be identified (blocks with "uses" and "with").

    Each matching block will then be refined by looking in the "with" block for
    a specific key and specific values, and if found, replaced inline with the
    given replacement.

    Here's an example with default values:

    .. code-block:: diff

          - uses: actions-rs/toolchain@v1
              with:
        -      profile: minimal
        +      profile: default
               toolchain: ${{ matrix.rust }}
               override: true
    """

    # Inherited variables, customized here
    language: str = "yaml"

    # DEBUG via website: https://ikatyang.github.io/tree-sitter-yaml/
    query: str = """
        (block_sequence_item
         (block_node
          (block_mapping
           (block_mapping_pair
            key: (flow_node (plain_scalar (string_scalar))))
           .
           (block_mapping_pair
            key: (flow_node (plain_scalar (string_scalar))))
           ))) @d
    """

    # Custom to this subclass:
    action_selector: str = "actions-rs/toolchain@v1"
    """The Github action to identify for parameter replacement"""
    with_key_target: str = "profile"
    """The selected action's parameter to target for replacement"""
    with_value_target: str = "minimal"
    """The "bad" value for with_key_target, which to replace"""
    replacement_value: str = "default"
    """The replacement value for the selected parameter"""

    def treesitter_query(self, captures) -> list[Node]:
        """Search the tree for compatible nodes"""
        print(f"Got {len(captures)} raw captures")
        matching_nodes = []
        for node, _name in captures:
            try:
                node_block = node.children[1]  # Children[0] is the "-" node
                kv_node = node_block.children[0]  # Down to block_mapping
                useswith_nodes = kv_node.children
                # Get the proper node, by keyword
                uses_node = [n for n in useswith_nodes if n.children[0].text == b"uses"]
                if not uses_node:
                    continue
                use_node = uses_node[0]
                # Assert value of kv
                if use_node.children[2].text != to_bytes(self.action_selector):
                    continue
                matching_nodes.append(useswith_nodes)
            except KeyError:
                continue  # Failing to grab the contents means bad keys = move on
        return matching_nodes

    def refine_search(self, matching_nodes) -> list[tuple[Node, Node]]:
        """Refine keyword matches

        Returns the nodes of key and value that should be edited.

        These are the nodes of "profile" and "minimal", when the "uses" keyword
        is set to "actions-rs/toolchain@v1".

        The exact "path" we wade through tree-sitter Nodes depends on parsed
        tree-structure (obviously) but also on tree-sitter language. Debugging
        is recommended via the Tree-Sitter Playground, in Query mode, exploring
        matches.
        """
        bad_k_v_nodes = []  # Bad as in worth editing
        for useswith_nodes in matching_nodes:
            try:
                with_nodes = [
                    n for n in useswith_nodes if n.children[0].text == b"with"
                ]
                if not with_nodes:
                    continue
                with_node = with_nodes[0]
                # Value of "key: value", -> down 1 -> list[kv]
                with_args = with_node.children[2].children[0].children
                # We know it's right block type: now check "with" (action args) for "badness"
                with_key_target_bytes = bytes(self.with_key_target, encoding="utf-8")
                target_key_nodes = [
                    n for n in with_args if n.children[0].text == with_key_target_bytes
                ]
                if not target_key_nodes:
                    continue
                target_key_node = target_key_nodes[0]
                target_value_nodes = target_key_node.children[2]
                if target_value_nodes.text != bytes(
                    self.with_value_target, encoding="utf-8"
                ):
                    continue  # Only the targeted parameter value should be replaced
                target_value_node = target_value_nodes.children[0]
                bad_k_v_nodes.append((target_key_node, target_value_node))
            except KeyError:
                continue  # Failing to grab the contents means bad keys = move on
        return bad_k_v_nodes

    def surgical_edit(self, text, bad_nodes: list[tuple[Node, Node]]) -> str:
        """Surgically edit the file to fix the badness

        In this case, we build a mutated line by using just the value we want,
        interpolated around the rest of the line.

        Particular attention is given to both beginning and end of original
        line, which could be housing some comments, which we don't want to edit.
        """
        mutated_lines = deepcopy(text).splitlines()
        for _k_node, v_node in bad_nodes:
            # Visualisation of old content:
            #      key: value
            #      ^ ^  ^   ^
            #      k0k1 v0  v1
            # k0_line, k0_col = k_node.start_point
            # k1_line, k1_col = k_node.end_point
            v0_line, v0_col = v_node.start_point
            _v1_line, v1_col = v_node.end_point
            bad_line = mutated_lines[v0_line]
            # New value
            #    key: REPLACED
            #         ^       ^
            # up to v0[       [v1 onwards
            replaced = self.replacement_value
            replaced_line = bad_line[:v0_col] + replaced + bad_line[v1_col:]
            mutated_lines[v0_line] = replaced_line
        return "\n".join(mutated_lines) + "\n"


def to_bytes(content: str):
    """Dump content string to bytes via utf-8"""
    return bytes(content, encoding="utf-8")
