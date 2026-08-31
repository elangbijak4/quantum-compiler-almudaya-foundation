"""
Module 7 Stage 3 — Statevector Simulator Engine.

Provides LocalReferenceStatevectorSimulator implementing ideal complex128 statevector evolution
for quantum circuits. Supported initial native gates: X, Y, Z, H, RX, RY, RZ, CNOT, CZ, SWAP.
"""

import math
import cmath
from typing import Dict, List, Tuple, Set, Optional, Any
from src.module7.stage3.model import ReferenceStatevectorSummary


class LocalReferenceStatevectorSimulator:
    """
    Ideal Complex128 Statevector Simulator.
    
    Invariants:
    1. Initial State: |0...0> (amplitude c_0 = 1.0, c_k = 0.0 for k > 0).
    2. Precision: COMPLEX128 (64-bit real + 64-bit imag).
    3. Normalization: Sum |c_k|^2 == 1.0 within numerical tolerance (1e-6).
    4. Bit Ordering: Qubit q0 is the least significant bit (LSB) of index k.
    """

    def __init__(self, num_qubits: int) -> None:
        if num_qubits <= 0 or num_qubits > 32:
            raise ValueError(f"EXECUTION_RESOURCE_EXHAUSTED: Invalid qubit count {num_qubits} (max 32).")
        self.num_qubits = num_qubits
        self.dim = 1 << num_qubits
        self.state: List[complex] = [0.0 + 0.0j] * self.dim
        self.state[0] = 1.0 + 0.0j

    def apply_single_qubit_gate(self, target_qubit: int, matrix: Tuple[Tuple[complex, complex], Tuple[complex, complex]]) -> None:
        """Applies a 2x2 unitary matrix to target_qubit."""
        bit_mask = 1 << target_qubit
        m00, m01 = matrix[0]
        m10, m11 = matrix[1]

        for i in range(self.dim):
            if (i & bit_mask) == 0:
                j = i | bit_mask
                v0 = self.state[i]
                v1 = self.state[j]
                self.state[i] = m00 * v0 + m01 * v1
                self.state[j] = m10 * v0 + m11 * v1

        self.verify_normalization()

    def apply_two_qubit_gate(self, control_qubit: int, target_qubit: int, matrix_4x4: List[List[complex]]) -> None:
        """Applies a 4x4 unitary matrix to control and target qubits."""
        ctrl_mask = 1 << control_qubit
        targ_mask = 1 << target_qubit

        for i in range(self.dim):
            if (i & ctrl_mask) == 0 and (i & targ_mask) == 0:
                i00 = i
                i01 = i | targ_mask
                i10 = i | ctrl_mask
                i11 = i | ctrl_mask | targ_mask

                vec = [self.state[i00], self.state[i01], self.state[i10], self.state[i11]]
                out = [0.0 + 0.0j] * 4

                for r in range(4):
                    out[r] = sum(matrix_4x4[r][c] * vec[c] for c in range(4))

                self.state[i00] = out[0]
                self.state[i01] = out[1]
                self.state[i10] = out[2]
                self.state[i11] = out[3]

        self.verify_normalization()

    def verify_normalization(self) -> None:
        """Verifies statevector norm is 1.0 within 1e-6 tolerance."""
        norm_sq = sum(abs(c) ** 2 for c in self.state)
        if abs(norm_sq - 1.0) > 1e-6:
            raise ValueError(f"STATE_EVOLUTION_FAILURE: Statevector normalization violated (norm^2 = {norm_sq:.9f}).")

    def execute_gate_sequence(self, gate_sequence: Tuple[Dict[str, Any], ...]) -> None:
        """Executes sequence of native operations in exact order."""
        for gate_info in gate_sequence:
            gate_name = gate_info["gate"]
            qubits = gate_info["qubits"]
            params = gate_info.get("params", {})

            if gate_name == "H":
                inv_sqrt2 = 1.0 / math.sqrt(2.0)
                h_mat = ((complex(inv_sqrt2, 0), complex(inv_sqrt2, 0)),
                         (complex(inv_sqrt2, 0), complex(-inv_sqrt2, 0)))
                self.apply_single_qubit_gate(qubits[0], h_mat)

            elif gate_name == "X":
                x_mat = ((0.0 + 0.0j, 1.0 + 0.0j),
                         (1.0 + 0.0j, 0.0 + 0.0j))
                self.apply_single_qubit_gate(qubits[0], x_mat)

            elif gate_name == "Y":
                y_mat = ((0.0 + 0.0j, 0.0 - 1.0j),
                         (0.0 + 1.0j, 0.0 + 0.0j))
                self.apply_single_qubit_gate(qubits[0], y_mat)

            elif gate_name == "Z":
                z_mat = ((1.0 + 0.0j, 0.0 + 0.0j),
                         (0.0 + 0.0j, -1.0 + 0.0j))
                self.apply_single_qubit_gate(qubits[0], z_mat)

            elif gate_name == "RX":
                theta = float(params.get("theta", 0.0))
                c = math.cos(theta / 2.0)
                s = math.sin(theta / 2.0)
                rx_mat = ((complex(c, 0), complex(0, -s)),
                          (complex(0, -s), complex(c, 0)))
                self.apply_single_qubit_gate(qubits[0], rx_mat)

            elif gate_name == "RY":
                theta = float(params.get("theta", 0.0))
                c = math.cos(theta / 2.0)
                s = math.sin(theta / 2.0)
                ry_mat = ((complex(c, 0), complex(-s, 0)),
                          (complex(s, 0), complex(c, 0)))
                self.apply_single_qubit_gate(qubits[0], ry_mat)

            elif gate_name == "RZ":
                phi = float(params.get("phi", 0.0))
                rz_mat = ((cmath.exp(complex(0, -phi / 2.0)), 0.0 + 0.0j),
                          (0.0 + 0.0j, cmath.exp(complex(0, phi / 2.0))))
                self.apply_single_qubit_gate(qubits[0], rz_mat)

            elif gate_name in ("CNOT", "CX"):
                ctrl, targ = qubits[0], qubits[1]
                cnot_mat = [
                    [1+0j, 0+0j, 0+0j, 0+0j],
                    [0+0j, 1+0j, 0+0j, 0+0j],
                    [0+0j, 0+0j, 0+0j, 1+0j],
                    [0+0j, 0+0j, 1+0j, 0+0j],
                ]
                self.apply_two_qubit_gate(ctrl, targ, cnot_mat)

            elif gate_name == "CZ":
                ctrl, targ = qubits[0], qubits[1]
                cz_mat = [
                    [1+0j, 0+0j, 0+0j, 0+0j],
                    [0+0j, 1+0j, 0+0j, 0+0j],
                    [0+0j, 0+0j, 1+0j, 0+0j],
                    [0+0j, 0+0j, 0+0j, -1+0j],
                ]
                self.apply_two_qubit_gate(ctrl, targ, cz_mat)

            elif gate_name == "SWAP":
                q0, q1 = qubits[0], qubits[1]
                swap_mat = [
                    [1+0j, 0+0j, 0+0j, 0+0j],
                    [0+0j, 0+0j, 1+0j, 0+0j],
                    [0+0j, 1+0j, 0+0j, 0+0j],
                    [0+0j, 0+0j, 0+0j, 1+0j],
                ]
                self.apply_two_qubit_gate(q0, q1, swap_mat)

            else:
                raise ValueError(f"UNSUPPORTED_NATIVE_GATE: Gate '{gate_name}' is not executable by local simulator.")

    def get_probabilities(self) -> Dict[str, float]:
        """Calculates exact computational basis probability distribution P(k) = |c_k|^2."""
        probs: Dict[str, float] = {}
        fmt_str = f"0{self.num_qubits}b"
        for i in range(self.dim):
            p = abs(self.state[i]) ** 2
            if p > 1e-12:
                bitstr = format(i, fmt_str)
                probs[bitstr] = float(p)
        return probs

    def get_statevector_summary(self) -> ReferenceStatevectorSummary:
        """Returns ReferenceStatevectorSummary."""
        probs = self.get_probabilities()
        return ReferenceStatevectorSummary(
            qubit_count=self.num_qubits,
            probabilities=probs,
        )
