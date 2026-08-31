"""
Module 2 Completion / Integration Package (Module 2 Stage 9).
"""

from .result import Module2CompletionResult
from .gate import (
    verify_module2_completion,
    _audit_stage_inventory,
    _audit_implementation_packages,
    _audit_canonical_ownership,
    _audit_duplicate_semantics,
    _audit_proof_boundary,
    _audit_certificate_boundary,
    _audit_quantum_boundary,
    _audit_documentation_portability,
    _audit_documentation_links,
    _audit_import_health,
)

__all__ = [
    "Module2CompletionResult",
    "verify_module2_completion",
    "_audit_stage_inventory",
    "_audit_implementation_packages",
    "_audit_canonical_ownership",
    "_audit_duplicate_semantics",
    "_audit_proof_boundary",
    "_audit_certificate_boundary",
    "_audit_quantum_boundary",
    "_audit_documentation_portability",
    "_audit_documentation_links",
    "_audit_import_health",
]
