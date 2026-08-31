"""
Module 6 Stage 5 — Extended Vocabulary Evaluator & Classification Engine.

Implements Hadamard extension experiment, superposition expansion, complex amplitude expansion,
redundancy testing, backward compatibility verification, and claim-vs-evidence classification.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Tuple, Set, Optional
import numpy as np
from src.module6.evolution.candidate import CandidateGate
from src.module6.evolution.target import TargetOperator, get_reference_target_hadamard
from src.module6.evolution.metrics import ExpressiveGainMetrics
from src.module6.evolution.provenance import Stage5Provenance


class ExtensionClassification(str, Enum):
    """
    Allowed Expressive Extension Classifications.
    """
    ALREADY_EXPRESSIBLE = "ALREADY_EXPRESSIBLE"
    REDUNDANT = "REDUNDANT"
    EMPIRICAL_EXTENSION = "EMPIRICAL_EXTENSION"
    PROVEN_EXTENSION = "PROVEN_EXTENSION"
    INCONCLUSIVE = "INCONCLUSIVE"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExtensionReport:
    """
    Detailed analytical report for a candidate gate extension experiment.
    """
    candidate_id: str
    candidate_name: str
    classification: str
    evidence_class: str
    metrics: ExpressiveGainMetrics
    hadamard_extension_pass: bool
    superposition_capability_extended: bool
    complex_amplitude_extended: bool
    redundancy_detected: bool
    backward_compatibility_pass: bool
    provenance: Stage5Provenance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "classification": str(self.classification),
            "evidence_class": str(self.evidence_class),
            "metrics": self.metrics.to_dict(),
            "hadamard_extension_pass": self.hadamard_extension_pass,
            "superposition_capability_extended": self.superposition_capability_extended,
            "complex_amplitude_extended": self.complex_amplitude_extended,
            "redundancy_detected": self.redundancy_detected,
            "backward_compatibility_pass": self.backward_compatibility_pass,
            "provenance": self.provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtensionReport":
        return cls(
            candidate_id=data["candidate_id"],
            candidate_name=data["candidate_name"],
            classification=data["classification"],
            evidence_class=data["evidence_class"],
            metrics=ExpressiveGainMetrics.from_dict(data["metrics"]),
            hadamard_extension_pass=data["hadamard_extension_pass"],
            superposition_capability_extended=data["superposition_capability_extended"],
            complex_amplitude_extended=data["complex_amplitude_extended"],
            redundancy_detected=data["redundancy_detected"],
            backward_compatibility_pass=data["backward_compatibility_pass"],
            provenance=Stage5Provenance.from_dict(data["provenance"]),
        )


class ExtendedVocabularyEvaluator:
    """
    Evaluator for Extended Gate Vocabulary experiments.
    """

    @classmethod
    def verify_hadamard_mathematics(cls, h_candidate: CandidateGate) -> Dict[str, Any]:
        """
        Mandatory Correction #1 — Hadamard Mathematics Verification:
        Verify H = 1/sqrt(2) * [[1, 1], [1, -1]]
        Verify H|0> = (|0> + |1>)/sqrt(2), H|1> = (|0> - |1>)/sqrt(2)
        Verify ||H|0>||_2 = 1.0, ||H|1>||_2 = 1.0, H^\dagger H = I within eps = 1e-12.
        """
        h_target = get_reference_target_hadamard()
        mat = h_candidate.matrix

        # Matrix distance to target H
        diff = np.linalg.norm(mat - h_target.matrix)
        matrix_match = float(diff) < 1e-12

        v0 = np.array([1.0, 0.0], dtype=complex)
        v1 = np.array([0.0, 1.0], dtype=complex)

        out0 = mat @ v0
        out1 = mat @ v1

        exp0 = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
        exp1 = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)

        match0 = float(np.linalg.norm(out0 - exp0)) < 1e-12
        match1 = float(np.linalg.norm(out1 - exp1)) < 1e-12

        norm0 = float(np.linalg.norm(out0))
        norm1 = float(np.linalg.norm(out1))

        u_dag = np.conjugate(mat.T)
        unitarity_res = float(np.linalg.norm(u_dag @ mat - np.eye(2, dtype=complex)))

        hadamard_pass = (
            matrix_match and match0 and match1 and
            abs(norm0 - 1.0) < 1e-12 and abs(norm1 - 1.0) < 1e-12 and
            unitarity_res < 1e-12
        )

        return {
            "hadamard_pass": hadamard_pass,
            "matrix_match": matrix_match,
            "h_v0_match": match0,
            "h_v1_match": match1,
            "norm_v0": norm0,
            "norm_v1": norm1,
            "unitarity_residual": unitarity_res,
        }

    @classmethod
    def evaluate_superposition_expansion(cls, candidate: CandidateGate) -> Tuple[bool, bool]:
        """
        Evaluates whether candidate gate enables basis state superposition.
        Returns (baseline_superposition, extended_superposition).
        Baseline G0 = {X, CNOT, TOFFOLI} has baseline_superposition = False.
        """
        # Baseline G0 generates no non-trivial superposition from basis inputs
        baseline_superpos = False

        # Test candidate on computational basis state |0>
        v0 = np.zeros(2 ** candidate.arity, dtype=complex)
        v0[0] = 1.0
        out = candidate.matrix @ v0

        non_zero_amplitudes = np.sum(np.abs(out) > 1e-12)
        extended_superpos = bool(non_zero_amplitudes > 1)

        return baseline_superpos, extended_superpos

    @classmethod
    def evaluate_complex_amplitude_expansion(cls, candidate: CandidateGate) -> Tuple[bool, bool]:
        """
        Evaluates whether candidate gate introduces complex (non-real) amplitudes.
        Returns (baseline_real_invariant, extended_real_invariant).
        Baseline G0 has real_invariant = True.
        """
        baseline_real_invariant = True

        # Check if candidate matrix contains non-zero imaginary components
        im_norm = float(np.linalg.norm(np.imag(candidate.matrix)))
        extended_real_invariant = not (im_norm > 1e-12)

        return baseline_real_invariant, extended_real_invariant

    @classmethod
    def evaluate_gate_redundancy(cls, candidate: CandidateGate) -> bool:
        """
        Evaluates whether candidate gate is expressible by baseline G0 = {X, CNOT, TOFFOLI}.
        Primitive gates X, CNOT, TOFFOLI, I, SWAP are expressible in G0 => redundant.
        Non-permutation gates (H, S, T, Rotations) are not in G0 => not redundant.
        """
        if candidate.name.upper() in ("X", "CNOT", "TOFFOLI", "I", "SWAP", "NOT"):
            return True

        # Check if candidate matrix is a permutation matrix
        mat = candidate.matrix
        dim = mat.shape[0]
        is_perm = True
        for r in range(dim):
            ones = np.sum(np.abs(mat[r, :]) > 1e-12)
            if ones != 1:
                is_perm = False
                break

        return is_perm

    @classmethod
    def evaluate_backward_compatibility(cls, g0_image: Set[str], g_ext_image: Set[str]) -> bool:
        """
        Enforces Img_N(F_G0) \subseteq Img_N(F_G').
        Returns True if all G0 image elements are in G_ext image elements.
        """
        return g0_image.issubset(g_ext_image)

    @classmethod
    def classify_extension(
        cls,
        candidate: CandidateGate,
        metrics: ExpressiveGainMetrics,
        is_redundant: bool,
        has_mathematical_proof: bool = False,
    ) -> Tuple[ExtensionClassification, str]:
        """
        Mandatory Correction #2 — Classifies extension result.
        |Img_N(F_G')| > |Img_N(F_G0)| gives EMPIRICAL_EXTENSION (or EXHAUSTIVE_FINITE_VERIFICATION).
        PROVEN_EXTENSION requires an explicit mathematical proof boolean flag `has_mathematical_proof=True`.
        Returns (classification_enum, evidence_class_str).
        """
        if is_redundant:
            return ExtensionClassification.REDUNDANT, "EMPIRICAL_EXPERIMENT"

        if metrics.expressive_gain_delta > 0:
            if has_mathematical_proof:
                return ExtensionClassification.PROVEN_EXTENSION, "STRUCTURAL_PROOF"
            else:
                return ExtensionClassification.EMPIRICAL_EXTENSION, "EMPIRICAL_EXPERIMENT"

        if metrics.expressive_gain_delta == 0:
            return ExtensionClassification.REDUNDANT, "EMPIRICAL_EXPERIMENT"

        return ExtensionClassification.INCONCLUSIVE, "INCONCLUSIVE"
