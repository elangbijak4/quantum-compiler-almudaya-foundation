"""
Module 6 Stage 2 — Image Signature Computation.

Calculates deterministic structural and semantic signatures for F(A) in Img_N(F).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module4.synthesis.verifier import execute_circuit_on_bitstring
from src.module6.classical.semantic import ClassicalSemanticModel


@dataclass(frozen=True)
class ImageSignature:
    """
    Deterministic signature representing F(A) in Img_N(F) and OpImg_N(F).
    """
    algorithm_id: str
    circuit_id: str
    classical_semantic_signature: str
    circuit_structural_signature: str
    operation_count: int
    gate_histogram: Dict[str, int]
    qubit_count: int
    operator_hash: str
    operator_equivalence_class_id: str


def compute_circuit_unitary(circuit: QuantumCircuitIR, max_qubits: int = 10) -> Optional[np.ndarray]:
    """
    Computes the exact dense unitary matrix U_F for a QuantumCircuitIR if total_qubits <= max_qubits.
    Returns None for total_qubits > max_qubits to prevent memory overflow.
    """
    total_qubits = sum(reg.width for reg in circuit.registers)
    if total_qubits > max_qubits:
        return None

    dim = 2 ** total_qubits
    matrix = np.zeros((dim, dim), dtype=complex)

    for col in range(dim):
        initial_bits = format(col, f"0{total_qubits}b")
        out_bits = execute_circuit_on_bitstring(circuit, initial_bits)
        row = int(out_bits, 2)
        matrix[row, col] = 1.0

    return matrix


def compute_image_signature(
    model: ClassicalSemanticModel,
    circuit: QuantumCircuitIR,
) -> ImageSignature:
    """
    Computes a deterministic ImageSignature for a classical model A and its compiled circuit F(A).
    """
    # 1. Classical Semantic Signature
    classical_sig = model.compute_deterministic_id()

    # 2. Circuit Structural Signature
    total_qubits = sum(reg.width for reg in circuit.registers)
    gate_types: List[str] = [g.gate_type.value for g in circuit.gates]
    gate_histogram: Dict[str, int] = {}
    for gt in gate_types:
        gate_histogram[gt] = gate_histogram.get(gt, 0) + 1

    sorted_hist = ",".join(f"{k}:{v}" for k, v in sorted(gate_histogram.items()))
    raw_structural = f"{circuit.circuit_id}|{total_qubits}|{len(circuit.gates)}|{sorted_hist}"
    structural_sig = hashlib.sha256(raw_structural.encode("utf-8")).hexdigest()

    # 3. Operator Matrix & Hash
    matrix = compute_circuit_unitary(circuit, max_qubits=10)

    if matrix is not None:
        mat_rows: List[str] = []
        for r in range(matrix.shape[0]):
            for c in range(matrix.shape[1]):
                val = matrix[r, c]
                mat_rows.append(f"{val.real:.12f}+{val.imag:.12f}i")
        raw_op = "|".join(mat_rows)
    else:
        sample_size = min(256, 2 ** total_qubits)
        sampled_rows: List[str] = []
        for col in range(sample_size):
            initial_bits = format(col, f"0{total_qubits}b")
            out_bits = execute_circuit_on_bitstring(circuit, initial_bits)
            sampled_rows.append(f"{initial_bits}->{out_bits}")
        raw_op = f"LARGE_CIRCUIT_{total_qubits}|" + "|".join(sampled_rows)

    op_hash = hashlib.sha256(raw_op.encode("utf-8")).hexdigest()
    eq_class_id = f"EQ_OP_{op_hash[:16]}"

    return ImageSignature(
        algorithm_id=model.algorithm_id,
        circuit_id=circuit.circuit_id,
        classical_semantic_signature=classical_sig,
        circuit_structural_signature=structural_sig,
        operation_count=len(circuit.gates),
        gate_histogram=gate_histogram,
        qubit_count=total_qubits,
        operator_hash=op_hash,
        operator_equivalence_class_id=eq_class_id,
    )
