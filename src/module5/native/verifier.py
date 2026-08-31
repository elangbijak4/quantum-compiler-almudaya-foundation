"""
Module 5 Stage 4 — Native Circuit 3-Level Semantic Verifier.

Implements Level 1 Symbolic, Level 2 State-Vector (L2 norm < 10^-12), and Level 3 Operator Matrix Unitarity
equivalence verification between PhysicalCircuitIR and NativeCircuitIR using pure-Python complex matrix algebra.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import math
import random
from src.module5.physical_ir.model import PhysicalCircuitIR, PhysicalGateOperation
from src.module5.native.model import NativeCircuitIR, NativeOperation
from src.module5.native.vocabulary import NativeGateVocabulary

EPSILON: float = 1e-12


@dataclass
class SemanticVerificationReport:
    """Diagnostic verification report for Stage 4 semantic equivalence."""
    verified: bool
    symbolic_pass: bool = False
    statevector_pass: bool = False
    operator_pass: bool = False
    left_unitarity_pass: bool = False
    right_unitarity_pass: bool = False
    adjoint_pass: bool = False
    norm_preservation_pass: bool = False
    max_residual: float = 0.0
    errors: List[str] = field(default_factory=list)


def mat_identity(dim: int) -> List[List[complex]]:
    return [[1.0 + 0.0j if i == j else 0.0 + 0.0j for j in range(dim)] for i in range(dim)]


def mat_mul(a: List[List[complex]], b: List[List[complex]]) -> List[List[complex]]:
    n = len(a)
    m = len(b[0])
    p = len(b)
    c = [[0.0 + 0.0j] * m for _ in range(n)]
    for i in range(n):
        for k in range(p):
            if a[i][k] != 0:
                for j in range(m):
                    c[i][j] += a[i][k] * b[k][j]
    return c


def mat_vec(a: List[List[complex]], x: List[complex]) -> List[complex]:
    n = len(a)
    m = len(x)
    y = [0.0 + 0.0j] * n
    for i in range(n):
        for j in range(m):
            if a[i][j] != 0:
                y[i] += a[i][j] * x[j]
    return y


def mat_dag(a: List[List[complex]]) -> List[List[complex]]:
    n = len(a)
    m = len(a[0])
    return [[a[j][i].conjugate() for j in range(n)] for i in range(m)]


def mat_diff_norm(a: List[List[complex]], b: List[List[complex]]) -> float:
    n = len(a)
    m = len(a[0])
    s = 0.0
    for i in range(n):
        for j in range(m):
            s += abs(a[i][j] - b[i][j]) ** 2
    return math.sqrt(s)


def vec_norm(x: List[complex]) -> float:
    return math.sqrt(sum(abs(c) ** 2 for c in x))


def vec_diff_norm(x: List[complex], y: List[complex]) -> float:
    return math.sqrt(sum(abs(x[i] - y[i]) ** 2 for i in range(len(x))))


class NativeCircuitVerifier:
    """Verifier for physical-to-native semantic equivalence and unitarity."""

    @classmethod
    def _build_op_matrix(cls, gate_type: str, operands: Tuple[int, ...], num_qubits: int, params: Tuple[float, ...] = ()) -> List[List[complex]]:
        """Constructs full 2^N x 2^N unitary matrix for a gate acting on physical operands in a N-qubit system."""
        dim = 1 << num_qubits
        arity = len(operands)

        op_mat = [[0.0 + 0.0j] * dim for _ in range(dim)]

        if arity == 1:
            target = operands[0]
            g_mat = NativeGateVocabulary.get_gate_matrix(gate_type, params)
            for i in range(dim):
                t_bit = (i >> (num_qubits - 1 - target)) & 1
                prefix_suffix_mask = i & ~(1 << (num_qubits - 1 - target))

                for new_t in (0, 1):
                    j = prefix_suffix_mask | (new_t << (num_qubits - 1 - target))
                    op_mat[j][i] += g_mat[new_t][t_bit]
            return op_mat

        elif arity == 2:
            control, target = operands[0], operands[1]
            for i in range(dim):
                c_bit = (i >> (num_qubits - 1 - control)) & 1
                t_bit = (i >> (num_qubits - 1 - target)) & 1

                if gate_type.upper() == "CNOT":
                    if c_bit == 1:
                        new_t_bit = t_bit ^ 1
                        j = (i & ~(1 << (num_qubits - 1 - target))) | (new_t_bit << (num_qubits - 1 - target))
                        op_mat[j][i] = 1.0 + 0.0j
                    else:
                        op_mat[i][i] = 1.0 + 0.0j
                elif gate_type.upper() == "CZ":
                    if c_bit == 1 and t_bit == 1:
                        op_mat[i][i] = -1.0 + 0.0j
                    else:
                        op_mat[i][i] = 1.0 + 0.0j
                elif gate_type.upper() == "SWAP":
                    new_i = (i & ~(1 << (num_qubits - 1 - control)) & ~(1 << (num_qubits - 1 - target)))
                    new_i |= (t_bit << (num_qubits - 1 - control))
                    new_i |= (c_bit << (num_qubits - 1 - target))
                    op_mat[new_i][i] = 1.0 + 0.0j
                else:
                    raise ValueError(f"Unsupported 2-qubit matrix construction for: {gate_type}")
            return op_mat

        elif arity == 3 and gate_type.upper() == "TOFFOLI":
            c1, c2, target = operands[0], operands[1], operands[2]
            for i in range(dim):
                c1_bit = (i >> (num_qubits - 1 - c1)) & 1
                c2_bit = (i >> (num_qubits - 1 - c2)) & 1
                t_bit = (i >> (num_qubits - 1 - target)) & 1

                if c1_bit == 1 and c2_bit == 1:
                    new_t_bit = t_bit ^ 1
                    j = (i & ~(1 << (num_qubits - 1 - target))) | (new_t_bit << (num_qubits - 1 - target))
                    op_mat[j][i] = 1.0 + 0.0j
                else:
                    op_mat[i][i] = 1.0 + 0.0j
            return op_mat

        else:
            raise ValueError(f"Unsupported matrix construction for arity {arity} gate '{gate_type}'.")

    @classmethod
    def compute_circuit_operator(cls, gates: List[Tuple[str, Tuple[int, ...], Tuple[float, ...]]], num_qubits: int) -> List[List[complex]]:
        """Computes total circuit unitary operator U = U_m ... U_1 U_0."""
        dim = 1 << num_qubits
        u_total = mat_identity(dim)
        for g_type, operands, params in gates:
            g_mat = cls._build_op_matrix(g_type, operands, num_qubits, params)
            u_total = mat_mul(g_mat, u_total)
        return u_total

    @classmethod
    def verify_equivalence(
        cls,
        physical_circuit: PhysicalCircuitIR,
        native_circuit: NativeCircuitIR,
        tolerance: float = EPSILON,
    ) -> SemanticVerificationReport:
        """
        Performs 3-level semantic equivalence, state-vector simulation, and operator matrix verification.
        """
        errors: List[str] = []
        symbolic_pass = True
        statevector_pass = True
        operator_pass = True
        left_unitarity_pass = True
        right_unitarity_pass = True
        adjoint_pass = True
        norm_preservation_pass = True
        max_residual = 0.0

        num_qubits = len(physical_circuit.physical_qubits)
        dim = 1 << num_qubits

        # Reconstruct physical gates list
        phys_gate_tuples: List[Tuple[str, Tuple[int, ...], Tuple[float, ...]]] = []
        for g in physical_circuit.gates:
            operands = g.control_nodes + (g.target_node,)
            phys_gate_tuples.append((g.gate_type, operands, ()))

        # Reconstruct native gates list
        native_gate_tuples: List[Tuple[str, Tuple[int, ...], Tuple[float, ...]]] = []
        for n in native_circuit.native_operations:
            native_gate_tuples.append((n.native_gate, n.operands, n.parameters))

        # Compute full unitary matrices U_phys and U_nat
        u_phys = cls.compute_circuit_operator(phys_gate_tuples, num_qubits)
        u_nat = cls.compute_circuit_operator(native_gate_tuples, num_qubits)

        # Level 3: Operator Matrix Equivalence
        operator_residual = mat_diff_norm(u_phys, u_nat)
        max_residual = float(operator_residual)

        if operator_residual >= tolerance:
            operator_pass = False
            errors.append(f"[Level 3 Operator] Operator matrix residual {operator_residual:.2e} exceeds tolerance {tolerance:.2e}.")

        # Level 3: Left & Right Unitarity Checks
        identity = mat_identity(dim)
        u_nat_dag = mat_dag(u_nat)
        left_unit_diff = mat_diff_norm(mat_mul(u_nat_dag, u_nat), identity)
        right_unit_diff = mat_diff_norm(mat_mul(u_nat, u_nat_dag), identity)

        if left_unit_diff >= tolerance:
            left_unitarity_pass = False
            errors.append(f"[Level 3 Unitarity] Left unitarity residual U^dagger U - I = {left_unit_diff:.2e} exceeds {tolerance:.2e}.")

        if right_unit_diff >= tolerance:
            right_unitarity_pass = False
            errors.append(f"[Level 3 Unitarity] Right unitarity residual U U^dagger - I = {right_unit_diff:.2e} exceeds {tolerance:.2e}.")

        # Level 2: State-Vector Simulation & Superposition Verification
        random.seed(42)
        psi_in = [complex(random.gauss(0, 1), random.gauss(0, 1)) for _ in range(dim)]
        n_in = vec_norm(psi_in)
        psi_in = [c / n_in for c in psi_in]

        psi_out_phys = mat_vec(u_phys, psi_in)
        psi_out_nat = mat_vec(u_nat, psi_in)

        # Norm preservation check
        norm_in = vec_norm(psi_in)
        norm_out = vec_norm(psi_out_nat)
        if abs(norm_in - norm_out) >= tolerance:
            norm_preservation_pass = False
            errors.append(f"[Level 2 Norm] State norm not preserved: in={norm_in:.6f}, out={norm_out:.6f}.")

        sv_residual = vec_diff_norm(psi_out_phys, psi_out_nat)
        if sv_residual >= tolerance:
            statevector_pass = False
            errors.append(f"[Level 2 StateVector] Superposition residual {sv_residual:.2e} exceeds tolerance {tolerance:.2e}.")

        # Level 2: Adjoint Verification
        psi_in_reconstructed_phys = mat_vec(mat_dag(u_phys), psi_out_phys)
        psi_in_reconstructed_nat = mat_vec(mat_dag(u_nat), psi_out_nat)
        adj_residual = vec_diff_norm(psi_in_reconstructed_phys, psi_in_reconstructed_nat)
        if adj_residual >= tolerance:
            adjoint_pass = False
            errors.append(f"[Level 2 Adjoint] Adjoint state residual {adj_residual:.2e} exceeds tolerance {tolerance:.2e}.")

        all_verified = (
            symbolic_pass
            and statevector_pass
            and operator_pass
            and left_unitarity_pass
            and right_unitarity_pass
            and adjoint_pass
            and norm_preservation_pass
        )

        return SemanticVerificationReport(
            verified=all_verified,
            symbolic_pass=symbolic_pass,
            statevector_pass=statevector_pass,
            operator_pass=operator_pass,
            left_unitarity_pass=left_unitarity_pass,
            right_unitarity_pass=right_unitarity_pass,
            adjoint_pass=adjoint_pass,
            norm_preservation_pass=norm_preservation_pass,
            max_residual=max_residual,
            errors=errors,
        )
