"""
Module 4 Stage 6 — Self-Auditing Integration & Completion Gate Data Models.

Defines structured completion status and master completion report for Module 4 Stage 6.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class Stage6CompletionStatus(str, Enum):
    """Completion status for Stage 6 Integration & Completion Gate."""
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class Stage6CompletionResult:
    """Master structured completion result for Stage 6 Self-Auditing Integration Gate."""
    status: Stage6CompletionStatus

    # Category Sub-Passes
    pipeline_pass: bool = False
    finite_domain_pass: bool = False
    encoding_pass: bool = False
    transition_pass: bool = False
    primitive_completeness_pass: bool = False
    decomposition_soundness_pass: bool = False
    ancilla_pass: bool = False
    bennett_uncomputation_pass: bool = False
    basis_equivalence_pass: bool = False
    superposition_pass: bool = False
    reverse_equivalence_pass: bool = False
    unitarity_pass: bool = False
    global_phase_pass: bool = False
    provenance_pass: bool = False
    determinism_pass: bool = False
    serialization_pass: bool = False
    negative_path_pass: bool = False
    frozen_integrity_pass: bool = False
    module5_boundary_pass: bool = False
    claim_evidence_pass: bool = False
    documentation_pass: bool = False
    regression_pass: bool = False

    # Numerical Residuals
    superposition_residual: float = 0.0
    left_unitarity_residual: float = 0.0
    right_unitarity_residual: float = 0.0

    diagnostics: List[str] = field(default_factory=list)
