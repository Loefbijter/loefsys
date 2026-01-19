"""Extension to help with the Django docs.

Intersphinx tries to find references for the Django docs in the wrong place. The
extension in this module corrects that.

The source of this extension was adapted from
`StackOverflow <https://stackoverflow.com/questions/62293058/>`_.
"""

from docutils.nodes import TextElement, document, reference
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.ext.intersphinx import missing_reference
from sphinx.util.typing import ExtensionMetadata


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up the extension.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.

    Returns
    -------
    ExtensionMetadata
        Metadata from this extension.
    """
    app.setup_extension("sphinx.ext.intersphinx")
    app.add_config_value("alias_mapping", {}, "env")
    app.connect("missing-reference", missing_reference_alias)
    app.connect("doctree-read", doctree_read_alias)
    return {"parallel_read_safe": True}


def missing_reference_alias(
    app: Sphinx, env: BuildEnvironment, node: pending_xref, contnode: TextElement
) -> reference | None:
    """Missing reference listener.

    Listen to missing references and apply an alias if found to subsequently provide to
    Intersphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.
    env : BuildEnvironment
        The build environment.
    node : pending_xref
        The node for which a reference is missing.
    contnode : TextElement
        The node that carries the text and formatting inside the future reference.
    """
    if _apply_alias(app, node):
        return missing_reference(app, env, node, contnode)
    return None


def doctree_read_alias(app: Sphinx, doctree: document) -> None:
    """Listen to doctree-read to find all missing nodes in the doctree.

    app : Sphinx
        The Sphinx application.
    doctree : document
        The doctree.

    Returns
    -------
    None
    """
    for node in doctree.findall(condition=pending_xref):
        _apply_alias(app, node)


def _apply_alias(app: Sphinx, node: pending_xref) -> bool:
    """Replace nodes with aliases.

    If an alias is provided for a missing reference, the values of the node are then
    changed to this alias.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application, used for retrieving the config value.
    node : pending_xref
        The missing reference.

    Returns
    -------
    bool
        ``True`` if an alias is found and replaced and ``False`` if no replacement was
        found.
    """
    reftarget = node.get("reftarget", None)
    alias_mapping = app.config.alias_mapping
    if not reftarget or not alias_mapping or reftarget not in alias_mapping:
        return False

    new_reftype, new_target = alias_mapping[reftarget]
    node["reftarget"] = new_target
    if new_reftype:
        *new_refdomain, new_reftype = new_reftype.split(":")
        node["reftype"] = new_reftype
        if new_refdomain:
            node["refdomain"] = new_refdomain[0]

    return True
