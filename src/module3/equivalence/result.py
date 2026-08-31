"""
Equivalence Verification Gate Data Models (Module 3 Stage 8).

Defines the three-valued verification gate result (PASS / FAIL / INCONCLUSIVE),
step result details, diagnostic failure localization, and provenance metadata.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any

from src.module3.qtm_ir.model import QTMIRStateVector, QTMIRProvenance


class EquivalenceStatus(str, Enum):
    """
    Three-valued verification gate outcome.
    """
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class EquivalenceStepResult:
    """
    Step-by-step verification result for step t in [0 ... T].
    """
    step: int
    classical_configuration: Any
    expected_basis_id: str
    quantum_state: QTMIRStateVector
    support_match: bool
    amplitude_match: bool
    identity_match: bool
    status: EquivalenceStatus
    classical_transition: Optional[str] = None
    quantum_transition: Optional[str] = None
    diagnostics: List[str] = field(default_factory=list)


@dataclass
class EquivalenceResult:
    """
    Master Equivalence Result containing three-valued outcome status, trace history,
    first failure localization, diagnostics, and provenance metadata.
    """
    status: EquivalenceStatus
    max_steps: int
    verified_steps: int
    first_failure_step: Optional[int] = None
    trace: List[EquivalenceStepResult] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    provenance: Optional[QTMIRProvenance] = None
