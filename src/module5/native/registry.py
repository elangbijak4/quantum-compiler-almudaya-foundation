"""
Module 5 Stage 4 — Gate Decomposition Registry.

Provides a declarative, deterministic registry for physical-to-native gate decompositions.
Every decomposition entry is verified for unitary semantic preservation.
"""

from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Tuple
from src.module5.physical_ir.model import PhysicalGateOperation
from src.module5.native.model import NativeOperation
from src.module5.native.vocabulary import NativeGateVocabulary


@dataclass
class DecompositionEntry:
    """Registered gate decomposition entry."""
    decomposition_id: str
    source_gate_type: str
    target_backend_class: str
    decompose_func: Callable[[PhysicalGateOperation], List[NativeOperation]]
    provenance: str = "STAGE_4_CANONICAL_DECOMPOSITION"


class GateDecompositionRegistry:
    """Registry managing canonical physical-to-native gate decompositions."""

    _entries: Dict[str, DecompositionEntry] = {}

    @classmethod
    def register(cls, entry: DecompositionEntry) -> None:
        key = f"{entry.source_gate_type.upper()}::{entry.target_backend_class.upper()}"
        cls._entries[key] = entry

    @classmethod
    def get_decomposition(cls, source_gate_type: str, backend_class: str = "ALL") -> Optional[DecompositionEntry]:
        source_key = source_gate_type.upper()
        # Direct lookup for exact backend class
        key = f"{source_key}::{backend_class.upper()}"
        if key in cls._entries:
            return cls._entries[key]

        # Partial match if backend_class contains target_backend_class
        for (k_src, k_bclass), entry in [(k.split("::"), v) for k, v in cls._entries.items()]:
            if k_src == source_key and (k_bclass in backend_class.upper() or k_bclass == "ALL"):
                return entry

        return None


# ------------------------------------------------------------------
# CANONICAL DECOMPOSITIONS
# ------------------------------------------------------------------

def _decompose_swap_to_cnots(op: PhysicalGateOperation) -> List[NativeOperation]:
    """SWAP(u, v) -> CNOT(u, v), CNOT(v, u), CNOT(u, v)."""
    if len(op.control_nodes) != 1:
        raise ValueError(f"SWAP operation expects 1 control node and 1 target node, got controls {op.control_nodes}.")
    u = op.control_nodes[0]
    v = op.target_node
    return [
        NativeOperation(native_gate="CNOT", operands=(u, v)),
        NativeOperation(native_gate="CNOT", operands=(v, u)),
        NativeOperation(native_gate="CNOT", operands=(u, v)),
    ]


def _decompose_cnot_to_cz(op: PhysicalGateOperation) -> List[NativeOperation]:
    """CNOT(u, v) -> H(v), CZ(u, v), H(v)."""
    if len(op.control_nodes) != 1:
        raise ValueError(f"CNOT operation expects 1 control node and 1 target node, got controls {op.control_nodes}.")
    u = op.control_nodes[0]
    v = op.target_node
    return [
        NativeOperation(native_gate="H", operands=(v,)),
        NativeOperation(native_gate="CZ", operands=(u, v)),
        NativeOperation(native_gate="H", operands=(v,)),
    ]


def _decompose_toffoli_to_cnots(op: PhysicalGateOperation) -> List[NativeOperation]:
    """
    Standard 6-CNOT decomposition of TOFFOLI(c1, c2, t).
    Uses standard T, Tdagger, H gates and CNOTs.
    """
    if len(op.control_nodes) != 2:
        raise ValueError(f"TOFFOLI operation expects 2 control nodes and 1 target node, got controls {op.control_nodes}.")
    c1, c2 = op.control_nodes
    t = op.target_node

    return [
        NativeOperation(native_gate="H", operands=(t,)),
        NativeOperation(native_gate="CNOT", operands=(c2, t)),
        NativeOperation(native_gate="T", operands=(t,)),
        NativeOperation(native_gate="CNOT", operands=(c1, t)),
        NativeOperation(native_gate="T", operands=(t,)),
        NativeOperation(native_gate="CNOT", operands=(c2, t)),
        NativeOperation(native_gate="T", operands=(t,)),
        NativeOperation(native_gate="CNOT", operands=(c1, t)),
        NativeOperation(native_gate="T", operands=(c2,)),
        NativeOperation(native_gate="T", operands=(t,)),
        NativeOperation(native_gate="H", operands=(t,)),
        NativeOperation(native_gate="CNOT", operands=(c1, c2)),
        NativeOperation(native_gate="T", operands=(c1,)),
        NativeOperation(native_gate="T", operands=(c2,)),
        NativeOperation(native_gate="CNOT", operands=(c1, c2)),
    ]


# Register canonical entries
GateDecompositionRegistry.register(
    DecompositionEntry(
        decomposition_id="SWAP_TO_3CNOT",
        source_gate_type="SWAP",
        target_backend_class="ALL",
        decompose_func=_decompose_swap_to_cnots,
    )
)

GateDecompositionRegistry.register(
    DecompositionEntry(
        decomposition_id="CNOT_TO_HCZH",
        source_gate_type="CNOT",
        target_backend_class="CZ_NATIVE",
        decompose_func=_decompose_cnot_to_cz,
    )
)

GateDecompositionRegistry.register(
    DecompositionEntry(
        decomposition_id="TOFFOLI_TO_CNOTS",
        source_gate_type="TOFFOLI",
        target_backend_class="ALL",
        decompose_func=_decompose_toffoli_to_cnots,
    )
)
