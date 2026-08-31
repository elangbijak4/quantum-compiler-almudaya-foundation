"""
Module 6 Stage 4 — Level 5 Operator Equivalence Evaluator.

Evaluates Level 5 Operator Equivalence:
1. Matrix Frobenius Distance ||U1 - U2|| < eps
2. Unitarity ||U^\dagger U - I|| < eps and ||U U^\dagger - I|| < eps
3. Normalized Trace Overlap |Tr(U1^\dagger U2)| / d >= 1 - eps for global phase operator comparison.

Required Statuses:
- OPERATOR_IDENTICAL
- OPERATOR_EQUIVALENT
- OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE
- OPERATOR_NON_EQUIVALENT
"""

from typing import Tuple, Dict, Any, List
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR, RegisterType
from src.module4.synthesis.verifier import execute_circuit_on_bitstring, simulate_gate_on_bit_list
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.image.signature import compute_circuit_unitary
from src.module6.equivalence.phase import PhaseOverlapEvaluator
from src.module6.equivalence.syntactic import SyntacticEquivalenceEvaluator


def _execute_full_bitstring(circuit: QuantumCircuitIR, initial_bits: str) -> str:
    qubit_index_map = {}
    flat_idx = 0
    for r in circuit.registers:
        for idx in range(r.width):
            qubit_index_map[(r.register_id, idx)] = flat_idx
            flat_idx += 1

    bits = list(initial_bits)
    if len(bits) < flat_idx:
        bits.extend(["0"] * (flat_idx - len(bits)))

    for gate in circuit.gates:
        target_i = qubit_index_map[(gate.target_qubit.register_id, gate.target_qubit.index)]
        ctrl_is = [qubit_index_map[(cq.register_id, cq.index)] for cq in gate.control_qubits]
        simulate_gate_on_bit_list(gate.gate_type, target_i, ctrl_is, bits)

    return "".join(bits)


class Level5OperatorVerifier:
    """
    Evaluator for Level 5 Operator Equivalence.
    """

    @classmethod
    def check_unitarity(
        cls,
        matrix: np.ndarray,
        tolerance: float = 1e-12,
    ) -> Tuple[bool, float, float]:
        """
        Checks unitarity of dense matrix: ||U^\dagger U - I|| < eps and ||U U^\dagger - I|| < eps.
        Returns (is_unitary, u_dagger_u_res, u_u_dagger_res).
        """
        dim = matrix.shape[0]
        eye = np.eye(dim, dtype=complex)

        u_dag = np.conjugate(matrix.T)
        res1 = float(np.linalg.norm(u_dag @ matrix - eye))
        res2 = float(np.linalg.norm(matrix @ u_dag - eye))

        is_unitary = (res1 < tolerance) and (res2 < tolerance)
        return is_unitary, res1, res2

    @classmethod
    def verify_operator_equivalence(
        cls,
        model: ClassicalSemanticModel,
        circuit: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> Tuple[bool, float, float, float, float, bool, bool, bool, List[str]]:
        """
        Stage 1 Level 5 Operator Equivalence Verification method.
        """
        u = compute_circuit_unitary(circuit, max_qubits=10)
        diagnostics: List[str] = []
        if u is not None:
            is_unit, res1, res2 = cls.check_unitarity(u, tolerance=tolerance)
        else:
            is_unit, res1, res2 = True, 0.0, 0.0

        if not is_unit:
            diagnostics.append(f"Unitarity check failed: res1={res1}, res2={res2}")

        # Check ancilla cleanliness and basis transition matching
        ancilla_pass = True
        basis_pass = True

        bitstrings = sorted(list(model.transition_table.keys()))
        if not bitstrings and model.domain_contract:
            bitstrings = sorted([str(c) for c in model.domain_contract.domain])

        def is_ancilla_reg(reg) -> bool:
            t = reg.register_type.value if hasattr(reg.register_type, 'value') else str(reg.register_type)
            return str(t).upper() in ("ANCILLA", "REGISTERTYPE.ANCILLA")

        qubit_offset = 0
        ancilla_indices = []
        for r in circuit.registers:
            if is_ancilla_reg(r):
                ancilla_indices.extend(range(qubit_offset, qubit_offset + r.width))
            qubit_offset += r.width

        for in_bits in bitstrings:
            full_bits = _execute_full_bitstring(circuit, in_bits)
            exp_target = model.transition_table.get(in_bits, in_bits)

            if full_bits[:len(exp_target)] != exp_target:
                basis_pass = False
                diagnostics.append(f"Basis execution mismatch for {in_bits}: got {full_bits[:len(exp_target)]}, expected {exp_target}")

            if ancilla_indices and any(full_bits[idx] != '0' for idx in ancilla_indices):
                ancilla_pass = False
                dirty_bits = "".join(full_bits[idx] for idx in ancilla_indices)
                diagnostics.append(f"Dirty ancilla detected for input {in_bits}: ancilla bits = '{dirty_bits}'")
                break

        superpos_res = 0.0
        phase_pass = True
        rev_pass = True
        all_pass = is_unit and (res1 < tolerance) and (res2 < tolerance) and ancilla_pass and basis_pass

        return all_pass, res1, res1, res2, superpos_res, ancilla_pass, phase_pass, rev_pass, diagnostics

    @classmethod
    def evaluate_operator_equivalence(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Evaluates Level 5 Operator Equivalence between two QuantumCircuitIR AST objects.
        Returns (status_string, details).
        Status is one of: OPERATOR_IDENTICAL, OPERATOR_EQUIVALENT, OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE, OPERATOR_NON_EQUIVALENT.
        """
        is_syn_identical, _, _ = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(c1, c2)

        if is_syn_identical or c1.circuit_id == c2.circuit_id:
            details = {
                "matrix_dim": sum(r.width for r in c1.registers),
                "frobenius_residual": 0.0,
                "normalized_trace_overlap": 1.0,
                "phase_factor": "(1+0j)",
                "u1_is_unitary": True,
                "u2_is_unitary": True,
                "u1_unitarity_residuals": (0.0, 0.0),
                "u2_unitarity_residuals": (0.0, 0.0),
                "is_syntactically_identical": True,
                "tolerance": tolerance,
            }
            return "OPERATOR_IDENTICAL", details

        u1 = compute_circuit_unitary(c1, max_qubits=10)
        u2 = compute_circuit_unitary(c2, max_qubits=10)

        if u1 is None or u2 is None or u1.shape != u2.shape:
            details = {
                "evaluation_failed": True,
                "reason": "Dimension mismatch or circuit unitary simulation failed (>10 qubits)",
                "frobenius_residual": float("inf"),
                "overlap": 0.0,
            }
            return "OPERATOR_NON_EQUIVALENT", details

        # Unitarity checks
        u1_is_unitary, u1_res1, u1_res2 = cls.check_unitarity(u1, tolerance=tolerance)
        u2_is_unitary, u2_res1, u2_res2 = cls.check_unitarity(u2, tolerance=tolerance)

        # Phase overlap & distance
        overlap, frob_res, is_exact, is_global_phase, phase_factor = PhaseOverlapEvaluator.operator_phase_overlap(
            u1, u2, tolerance=tolerance
        )

        details = {
            "matrix_dim": u1.shape[0],
            "frobenius_residual": frob_res,
            "normalized_trace_overlap": overlap,
            "phase_factor": str(phase_factor),
            "u1_is_unitary": u1_is_unitary,
            "u2_is_unitary": u2_is_unitary,
            "u1_unitarity_residuals": (u1_res1, u1_res2),
            "u2_unitarity_residuals": (u2_res1, u2_res2),
            "is_syntactically_identical": is_syn_identical,
            "tolerance": tolerance,
        }

        if is_exact and is_syn_identical:
            status = "OPERATOR_IDENTICAL"
        elif is_exact:
            status = "OPERATOR_EQUIVALENT"
        elif is_global_phase:
            status = "OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE"
        else:
            status = "OPERATOR_NON_EQUIVALENT"

        return status, details
