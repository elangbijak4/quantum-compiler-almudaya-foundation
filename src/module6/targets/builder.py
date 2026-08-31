"""
Module 6 Stage 2 — Target Catalog Builder.

Constructs standardized target operator families T_U and target circuit families T_C.
Must include Hadamard (H) treated as a target candidate and open hypothesis.
"""

from typing import List, Dict, Tuple
import numpy as np
from src.module6.targets.catalog import TargetClassification, TargetOperator, TargetCircuit


class TargetCatalogBuilder:
    """
    Builder for standard target operator families T_U and circuit families T_C.
    """

    @classmethod
    def build_default_target_operators(cls) -> List[TargetOperator]:
        """
        Builds default target operator catalog T_U.
        """
        targets: List[TargetOperator] = []

        # 1. Pauli-X (1 qubit)
        x_mat = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_X",
                qubit_count=1,
                matrix=x_mat,
                classification=TargetClassification.PRIMITIVE_GATE,
                provenance="PAULI_X_PRIMITIVE",
            )
        )

        # 2. Pauli-Z (1 qubit)
        z_mat = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_Z",
                qubit_count=1,
                matrix=z_mat,
                classification=TargetClassification.SINGLE_QUBIT,
                provenance="PAULI_Z_SINGLE_QUBIT",
            )
        )

        # 3. CNOT (2 qubits)
        cnot_mat = np.eye(4, dtype=complex)
        cnot_mat[2:4, 2:4] = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_CNOT",
                qubit_count=2,
                matrix=cnot_mat,
                classification=TargetClassification.ENTANGLING,
                provenance="CNOT_PRIMITIVE",
            )
        )

        # 4. SWAP (2 qubits)
        swap_mat = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
        ], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_SWAP",
                qubit_count=2,
                matrix=swap_mat,
                classification=TargetClassification.MULTI_QUBIT_REVERSIBLE,
                provenance="SWAP_REVERSIBLE",
            )
        )

        # 5. TOFFOLI (3 qubits)
        toffoli_mat = np.eye(8, dtype=complex)
        toffoli_mat[6:8, 6:8] = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_TOFFOLI",
                qubit_count=3,
                matrix=toffoli_mat,
                classification=TargetClassification.MULTI_QUBIT_REVERSIBLE,
                provenance="TOFFOLI_PRIMITIVE",
            )
        )

        # 6. Hadamard H (1 qubit) — OPEN HYPOTHESIS
        h_mat = (1.0 / np.sqrt(2.0)) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_H",
                qubit_count=1,
                matrix=h_mat,
                classification=TargetClassification.SUPERPOSITION_TRANSFORMATION,
                provenance="HADAMARD_SUPERPOSITION",
                is_open_hypothesis=True,
            )
        )

        # 7. Phase S gate (1 qubit)
        s_mat = np.array([[1.0, 0.0], [0.0, 1j]], dtype=complex)
        targets.append(
            TargetOperator(
                target_id="target_S",
                qubit_count=1,
                matrix=s_mat,
                classification=TargetClassification.SINGLE_QUBIT,
                provenance="PHASE_S_SINGLE_QUBIT",
            )
        )

        return targets

    @classmethod
    def build_default_target_circuits(cls) -> List[TargetCircuit]:
        """
        Builds default target circuit catalog T_C.
        """
        op_targets = cls.build_default_target_operators()
        op_dict = {t.target_id: t for t in op_targets}

        circuits: List[TargetCircuit] = []

        if "target_X" in op_dict:
            circuits.append(
                TargetCircuit(
                    target_id="circuit_X",
                    qubit_count=1,
                    gate_sequence=("X[0]",),
                    target_operator=op_dict["target_X"],
                    classification=TargetClassification.PRIMITIVE_GATE,
                )
            )

        if "target_CNOT" in op_dict:
            circuits.append(
                TargetCircuit(
                    target_id="circuit_CNOT",
                    qubit_count=2,
                    gate_sequence=("CNOT[0,1]",),
                    target_operator=op_dict["target_CNOT"],
                    classification=TargetClassification.ENTANGLING,
                )
            )

        if "target_H" in op_dict:
            circuits.append(
                TargetCircuit(
                    target_id="circuit_H",
                    qubit_count=1,
                    gate_sequence=("H[0]",),
                    target_operator=op_dict["target_H"],
                    classification=TargetClassification.SUPERPOSITION_TRANSFORMATION,
                )
            )

        return circuits
