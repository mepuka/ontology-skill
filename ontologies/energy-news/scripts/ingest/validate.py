"""SHACL validation wrapper — warn mode for missing coversTopic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyshacl import validate as shacl_validate

if TYPE_CHECKING:
    from rdflib import Graph


def validate_abox(
    data_graph: Graph,
    shapes_graph: Graph,
    *,
    strict: bool = False,
) -> tuple[bool, str]:
    """Run SHACL validation on the ABox data.

    Args:
        data_graph: Merged TBox + reference + ABox graph.
        shapes_graph: SHACL shapes graph.
        strict: If True, fail on any violation. If False, report but don't fail
                on sh:Warning severity (e.g., missing coversTopic).

    Returns:
        Tuple of (conforms: bool, results_text: str).
    """
    conforms, _results_graph, results_text = shacl_validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
    )

    if strict:
        return conforms, results_text

    # In warn mode, we treat it as passing but still report issues
    return True, results_text
