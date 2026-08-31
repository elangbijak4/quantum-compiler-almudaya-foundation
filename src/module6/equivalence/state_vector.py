"""
Module 6 Stage 4 — Level 4 State-Vector Equivalence Evaluator.

Evaluates ||psi1 - psi2||_2 < eps (EXACT_STATE_EQUIVALENCE) and |<psi1|psi2>| >= 1 - eps (GLOBAL_PHASE_EQUIVALENCE).
Evaluates state-vector test suite across computational basis, uniform real superposition, deterministic random real states,
and deterministic random complex states using local PRNG seed.
"""

from typing import Tuple, Dict, Any, List
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.image.signature import compute_circuit_unitary
from src.module6.equivalence.phase import PhaseOverlapEvaluator


class StateVectorEquivalenceEvaluator:
    """
    Evaluator for Level 4 State-Vector Equivalence.
    """

    @classmethod
    def generate_test_states(
        cls,
        num_qubits: int,
        seed: int = 42,
    ) -> List[Tuple[str, np.ndarray]]:
        """
        Generates deterministic test suite of normalized state vectors:
        1. Basis states (|0...0>, |0...1>, ...)
        2. Uniform real superposition (|+...+>)
        3. Deterministic random real states
        4. Deterministic random complex states
        """
        dim = 2 ** num_qubits
        rng = np.random.RandomState(seed)
        test_states: List[Tuple[str, np.ndarray]] = []

        # 1. Computational Basis States
        max_basis = min(dim, 16)
        for i in range(max_basis):
            vec = np.zeros(dim, dtype=complex)
            vec[i] = 1.0
            test_states.append((f"basis_{i}", vec))

        # 2. Uniform Real Superposition
        vec_super = np.ones(dim, dtype=complex) / np.sqrt(dim)
        test_states.append(("uniform_superposition", vec_super))

        # 3. Deterministic Random Real State
        r_vec = rng.randn(dim).astype(complex)
        r_vec /= np.linalg.norm(r_vec)
        test_states.append(("random_real", r_vec))

        # 4. Deterministic Random Complex State
        c_vec = rng.randn(dim) + 1j * rng.randn(dim)
        c_vec /= np.linalg.norm(c_vec)
        test_states.append(("random_complex", c_vec))

        return test_states

    @classmethod
    def evaluate_state_vector_equivalence(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        seed: int = 42,
        tolerance: float = 1e-12,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Evaluates Level 4 State-Vector Equivalence over test states suite.
        Returns (status_string, details).
        Status is one of: EXACT_STATE_EQUIVALENCE, GLOBAL_PHASE_EQUIVALENCE, STATE_NON_EQUIVALENCE.
        """
        u1 = compute_circuit_unitary(c1, max_qubits=10)
        u2 = compute_circuit_unitary(c2, max_qubits=10)

        if u1 is None or u2 is None or u1.shape != u2.shape:
            details = {
                "evaluation_failed": True,
                "reason": "Dimension mismatch or circuit unitary simulation failed (>10 qubits)",
                "seed": seed,
            }
            return "STATE_NON_EQUIVALENCE", details

        num_qubits = int(np.log2(u1.shape[0]))
        test_states = cls.generate_test_states(num_qubits, seed=seed)

        all_exact = True
        all_phase = True
        max_l2_res = 0.0
        min_overlap = 1.0
        state_results: List[Dict[str, Any]] = []

        for name, vec in test_states:
            psi1 = u1 @ vec
            psi2 = u2 @ vec

            overlap, l2_res, is_exact, is_phase = PhaseOverlapEvaluator.state_phase_overlap(
                psi1, psi2, tolerance=tolerance
            )

            max_l2_res = max(max_l2_res, l2_res)
            min_overlap = min(min_overlap, overlap)

            if not is_exact:
                all_exact = False
            if not is_phase:
                all_phase = False

            state_results.append(
                {
                    "state_name": name,
                    "l2_residual": l2_res,
                    "overlap": overlap,
                    "exact_match": is_exact,
                    "global_phase_match": is_phase,
                }
            )

        details = {
            "num_qubits": num_qubits,
            "seed": seed,
            "states_tested_count": len(test_states),
            "max_l2_residual": max_l2_res,
            "min_overlap": min_overlap,
            "all_exact_equal": all_exact,
            "all_global_phase_equal": all_phase,
            "state_results": state_results,
        }

        if all_exact:
            status = "EXACT_STATE_EQUIVALENCE"
        elif all_phase:
            status = "GLOBAL_PHASE_EQUIVALENCE"
        else:
            status = "STATE_NON_EQUIVALENCE"

        return status, details
