"""
Module 5 Stage 4 — Native Gate Vocabulary Definitions & Matrix Providers.

Defines canonical native gate definitions and exact pure-Python complex matrix providers for semantic verification.
"""

from typing import Dict, Optional, List, Tuple
import math
import cmath
from src.module5.native.model import NativeGateDefinition


class NativeGateVocabulary:
    """Canonical native gate definitions library."""

    X = NativeGateDefinition(gate_id="X", gate_name="Pauli-X", arity=1, parameter_count=0)
    Y = NativeGateDefinition(gate_id="Y", gate_name="Pauli-Y", arity=1, parameter_count=0)
    Z = NativeGateDefinition(gate_id="Z", gate_name="Pauli-Z", arity=1, parameter_count=0)
    H = NativeGateDefinition(gate_id="H", gate_name="Hadamard", arity=1, parameter_count=0)
    S = NativeGateDefinition(gate_id="S", gate_name="Phase-S", arity=1, parameter_count=0)
    T = NativeGateDefinition(gate_id="T", gate_name="Phase-T", arity=1, parameter_count=0)
    SX = NativeGateDefinition(gate_id="SX", gate_name="Sqrt-X", arity=1, parameter_count=0)
    RZ = NativeGateDefinition(gate_id="RZ", gate_name="Rotation-Z", arity=1, parameter_count=1)

    CNOT = NativeGateDefinition(gate_id="CNOT", gate_name="Controlled-NOT", arity=2, parameter_count=0)
    CZ = NativeGateDefinition(gate_id="CZ", gate_name="Controlled-Z", arity=2, parameter_count=0)
    SWAP = NativeGateDefinition(gate_id="SWAP", gate_name="SWAP", arity=2, parameter_count=0)
    TOFFOLI = NativeGateDefinition(gate_id="TOFFOLI", gate_name="Toffoli", arity=3, parameter_count=0)

    @classmethod
    def get_standard_vocabulary(cls) -> Dict[str, NativeGateDefinition]:
        """Returns standard native gate dictionary."""
        return {
            "X": cls.X,
            "Y": cls.Y,
            "Z": cls.Z,
            "H": cls.H,
            "S": cls.S,
            "T": cls.T,
            "SX": cls.SX,
            "RZ": cls.RZ,
            "CNOT": cls.CNOT,
            "CZ": cls.CZ,
            "SWAP": cls.SWAP,
            "TOFFOLI": cls.TOFFOLI,
        }

    @classmethod
    def get_gate_matrix(cls, gate_name: str, params: Tuple[float, ...] = ()) -> List[List[complex]]:
        """Returns exact complex unitary matrix for standard native gates as List[List[complex]]."""
        name = gate_name.upper()
        if name == "X":
            return [[0.0, 1.0], [1.0, 0.0]]
        elif name == "Y":
            return [[0.0, -1j], [1j, 0.0]]
        elif name == "Z":
            return [[1.0, 0.0], [0.0, -1.0]]
        elif name == "H":
            inv_sqrt2 = 1.0 / math.sqrt(2)
            return [[inv_sqrt2, inv_sqrt2], [inv_sqrt2, -inv_sqrt2]]
        elif name == "S":
            return [[1.0, 0.0], [0.0, 1j]]
        elif name == "T":
            return [[1.0, 0.0], [0.0, cmath.exp(1j * math.pi / 4)]]
        elif name == "SX":
            return [[0.5 * (1 + 1j), 0.5 * (1 - 1j)], [0.5 * (1 - 1j), 0.5 * (1 + 1j)]]
        elif name == "RZ":
            theta = params[0] if params else 0.0
            return [[cmath.exp(-1j * theta / 2), 0.0], [0.0, cmath.exp(1j * theta / 2)]]
        elif name == "CNOT":
            return [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0, 0.0],
            ]
        elif name == "CZ":
            return [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, -1.0],
            ]
        elif name == "SWAP":
            return [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        elif name == "TOFFOLI":
            mat = [[0.0 + 0.0j] * 8 for _ in range(8)]
            for i in range(6):
                mat[i][i] = 1.0 + 0.0j
            mat[6][7] = 1.0 + 0.0j
            mat[7][6] = 1.0 + 0.0j
            return mat
        else:
            raise ValueError(f"Unknown matrix for gate: {gate_name}")
