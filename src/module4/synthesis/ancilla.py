"""
Module 4 Stage 3 — Workspace Ancilla Allocation & Bennett Uncomputation Protocol.

Manages physical workspace ancillas in QuantumCircuitIR and tracks clean (|0>) status before and after gate synthesis.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set, Optional
from src.module4.circuit_ir.model import (
    QubitRegister,
    QubitRef,
    GateOperation,
    AncillaDeclaration,
    AncillaStatus,
    RegisterType,
    LogicalGateType,
)


@dataclass
class AncillaManager:
    """
    Manages workspace ancillas allocated for logical gate synthesis.
    
    Guarantees Bennett Uncomputation Protocol:
    1. Compute temporary workspace value (Toffoli AND-tree)
    2. Use temporary value on target qubit (X, CNOT, or Toffoli)
    3. Uncompute temporary workspace (Reversed Toffoli AND-tree)
    4. Verify all workspace ancillas return cleanly to |0>
    """
    ancilla_register: QubitRegister
    allocated_count: int = 0
    active_ancillas: List[QubitRef] = field(default_factory=list)

    def allocate_ancilla(self) -> QubitRef:
        """Allocates a fresh workspace ancilla initialized to |0>."""
        if self.allocated_count >= self.ancilla_register.width:
            raise RuntimeError(f"Ancilla allocation exceeded register width {self.ancilla_register.width}.")
        ref = self.ancilla_register.get_qubit_ref(self.allocated_count)
        self.allocated_count += 1
        self.active_ancillas.append(ref)
        return ref

    def build_ancilla_declarations(self) -> List[AncillaDeclaration]:
        """Generates AncillaDeclarations for all allocated ancillas verifying CLEAN status."""
        declarations = []
        for ref in self.active_ancillas:
            declarations.append(
                AncillaDeclaration(
                    qubit_ref=ref,
                    initial_status=AncillaStatus.CLEAN,
                    expected_final_status=AncillaStatus.CLEAN,
                )
            )
        return declarations


def synthesize_multi_controlled_not(
    controls: List[QubitRef],
    control_values: List[str],  # '1' or '0'
    target: QubitRef,
    ancilla_mgr: AncillaManager,
    current_gate_index: int,
) -> Tuple[List[GateOperation], int]:
    """
    Synthesizes a multi-controlled NOT operation conditioned on controls == control_values.
    
    Uses Bennett Uncomputation Protocol to ensure ALL workspace ancillas return cleanly to |0>.
    Returns (gate_operations, next_gate_index).
    """
    gates: List[GateOperation] = []
    idx = current_gate_index

    # 1. Apply X to controls where control value is '0'
    inverted_controls: Set[QubitRef] = set()
    for ctrl, val in zip(controls, control_values):
        if val == "0":
            gates.append(GateOperation(gate_type=LogicalGateType.X, target_qubit=ctrl, operation_index=idx))
            idx += 1
            inverted_controls.add(ctrl)

    n_ctrl = len(controls)

    if n_ctrl == 0:
        # Unconditional X
        gates.append(GateOperation(gate_type=LogicalGateType.X, target_qubit=target, operation_index=idx))
        idx += 1
    elif n_ctrl == 1:
        # CNOT
        gates.append(GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(controls[0],), target_qubit=target, operation_index=idx))
        idx += 1
    elif n_ctrl == 2:
        # Standard Toffoli
        gates.append(GateOperation(gate_type=LogicalGateType.TOFFOLI, control_qubits=(controls[0], controls[1]), target_qubit=target, operation_index=idx))
        idx += 1
    else:
        # k > 2 controls: Build AND-tree with workspace ancillas + Bennett Uncomputation
        ancilla_tree: List[QubitRef] = []
        compute_gates: List[GateOperation] = []

        # Step A: Compute AND-tree
        # First layer: controls[0] AND controls[1] -> a0
        a0 = ancilla_mgr.allocate_ancilla()
        ancilla_tree.append(a0)
        compute_gates.append(GateOperation(gate_type=LogicalGateType.TOFFOLI, control_qubits=(controls[0], controls[1]), target_qubit=a0, operation_index=idx))
        idx += 1

        # Intermediate layers: a_{i-1} AND controls[i+1] -> a_i
        for c_idx in range(2, n_ctrl):
            a_next = ancilla_mgr.allocate_ancilla()
            ancilla_tree.append(a_next)
            compute_gates.append(GateOperation(gate_type=LogicalGateType.TOFFOLI, control_qubits=(ancilla_tree[-2], controls[c_idx]), target_qubit=a_next, operation_index=idx))
            idx += 1

        # Append compute gates
        gates.extend(compute_gates)

        # Step B: Apply target operation using root ancilla
        root_ancilla = ancilla_tree[-1]
        gates.append(GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(root_ancilla,), target_qubit=target, operation_index=idx))
        idx += 1

        # Step C: Bennett Uncomputation (reverse compute gates in exact opposite order)
        for c_gate in reversed(compute_gates):
            gates.append(GateOperation(gate_type=c_gate.gate_type, control_qubits=c_gate.control_qubits, target_qubit=c_gate.target_qubit, operation_index=idx))
            idx += 1

    # 2. Re-apply X to restore inverted control qubits
    for ctrl in controls:
        if ctrl in inverted_controls:
            gates.append(GateOperation(gate_type=LogicalGateType.X, target_qubit=ctrl, operation_index=idx))
            idx += 1

    return gates, idx
