"""
Module 5 Stage 3 — Semantic Preservation & Post-Routing Invariant Verifier.

Verifies input logical circuit immutability, mapping injectivity, physical node bounds,
topology edge satisfaction for all physical gates, and structural integrity of the routed PhysicalCircuitIR.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module5.physical_ir.model import (
    PhysicalCircuitIR,
    QubitMapping,
    DeviceTopology,
)
from src.module5.physical_ir.validator import validate_physical_circuit_ir
from src.module5.physicalization.trace import RoutingTrace


@dataclass
class PhysicalizationVerificationResult:
    """Diagnostic verification report for Stage 3 Physicalization."""
    verified: bool
    input_unmutated: bool = False
    mapping_injective: bool = False
    topology_satisfied: bool = False
    ir_valid: bool = False
    errors: List[str] = field(default_factory=list)


class SemanticPreservationVerifier:
    """Verifier for Stage 3 physicalization invariants and logical circuit immutability."""

    @classmethod
    def verify(
        cls,
        input_circuit: QuantumCircuitIR,
        input_circuit_snapshot_hash: int,
        physical_circuit: PhysicalCircuitIR,
        final_mapping: QubitMapping,
        topology: DeviceTopology,
        trace: Optional[RoutingTrace] = None,
    ) -> PhysicalizationVerificationResult:
        """
        Executes comprehensive post-routing verification.
        Does NOT modify any circuit or mapping objects.
        """
        errors: List[str] = []
        input_unmutated = True
        mapping_injective = True
        topology_satisfied = True
        ir_valid = True

        # 1. Verify input QuantumCircuitIR was not mutated (compare string representation hash)
        current_hash = hash(str(input_circuit))
        if current_hash != input_circuit_snapshot_hash:
            input_unmutated = False
            errors.append("Verification failure: Input QuantumCircuitIR was mutated during physicalization.")

        # 2. Verify mapping injectivity
        if not final_mapping.is_injective():
            mapping_injective = False
            errors.append("Verification failure: Final QubitMapping is non-injective.")

        # 3. Verify all physical gates in PhysicalCircuitIR satisfy topology connectivity
        for gate in physical_circuit.gates:
            nodes = gate.control_nodes + (gate.target_node,)
            if len(nodes) == 2:
                u, v = nodes
                if not topology.is_connected(u, v):
                    topology_satisfied = False
                    errors.append(
                        f"Verification failure: Physical gate '{gate.gate_type}' at operation_index {gate.operation_index} violates topology connectivity for physical nodes ({u}, {v})."
                    )

        # 4. Verify PhysicalCircuitIR using Stage 1 validator
        val_res = validate_physical_circuit_ir(physical_circuit)
        if not val_res.valid:
            ir_valid = False
            errors.extend([f"Verification failure (Stage 1 validator): {e}" for e in val_res.errors])

        all_ok = input_unmutated and mapping_injective and topology_satisfied and ir_valid

        return PhysicalizationVerificationResult(
            verified=all_ok,
            input_unmutated=input_unmutated,
            mapping_injective=mapping_injective,
            topology_satisfied=topology_satisfied,
            ir_valid=ir_valid,
            errors=errors,
        )
