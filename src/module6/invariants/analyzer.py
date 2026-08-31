"""
Module 6 Stage 3 — Master Structural Invariant Analyzer.

Executes all structural invariant analyzers (permutation, real amplitude, superposition, composition, inverse, identity).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.mapping.model import BoundClassification
from src.module6.invariants.permutation import PermutationInvariantAnalyzer
from src.module6.invariants.amplitude import RealAmplitudeInvariantAnalyzer
from src.module6.invariants.composition import (
    SuperpositionCapabilityAnalyzer,
    CompositionClosureAnalyzer,
    InverseClosureAnalyzer,
    IdentityElementAnalyzer,
)


@dataclass(frozen=True)
class StructuralInvariantResult:
    """
    Immutable summary result of all Stage 3 structural invariant analyses.
    """
    permutation_invariant_status: str
    permutation_invariant_classification: BoundClassification
    real_amplitude_status: str
    real_amplitude_classification: BoundClassification
    superposition_status: str
    superposition_generates: bool
    composition_closure_status: str
    inverse_closure_status: str
    identity_status: str
    identity_circuit_id: Optional[str]
    provenance: Dict[str, str] = field(default_factory=dict)


class StructuralInvariantAnalyzer:
    """
    Master analyzer running all structural invariant checks.
    """

    @classmethod
    def analyze_structural_invariants(
        cls,
        circuits: List[QuantumCircuitIR],
        tolerance: float = 1e-12,
    ) -> StructuralInvariantResult:
        """
        Runs permutation, real amplitude, superposition, composition, inverse, and identity invariant checks.
        """
        p_status, p_class, _ = PermutationInvariantAnalyzer.analyze_permutation_invariant(circuits, tolerance=tolerance)
        r_status, r_class, _ = RealAmplitudeInvariantAnalyzer.analyze_real_amplitude_invariant(circuits, tolerance=tolerance)
        s_status, s_gen, _ = SuperpositionCapabilityAnalyzer.test_superposition_capability(circuits)
        comp_status, _, _ = CompositionClosureAnalyzer.analyze_composition_closure(circuits)
        inv_status, _, _ = InverseClosureAnalyzer.analyze_inverse_closure(circuits)
        id_status, id_circ, _ = IdentityElementAnalyzer.analyze_identity_element(circuits)

        prov = {
            "module": "module6",
            "stage": "stage3",
            "permutation_invariant": p_status,
            "real_amplitude_invariant": r_status,
        }

        return StructuralInvariantResult(
            permutation_invariant_status=p_status,
            permutation_invariant_classification=p_class,
            real_amplitude_status=r_status,
            real_amplitude_classification=r_class,
            superposition_status=s_status,
            superposition_generates=s_gen,
            composition_closure_status=comp_status,
            inverse_closure_status=inv_status,
            identity_status=id_status,
            identity_circuit_id=id_circ,
            provenance=prov,
        )
