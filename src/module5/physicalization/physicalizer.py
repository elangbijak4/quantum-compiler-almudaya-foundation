"""
Module 5 Stage 3 — Main Physicalization & SWAP Routing Engine.

Transforms a logically valid QuantumCircuitIR into a topology-compatible PhysicalCircuitIR.
Inserts physical SWAP operations where required by topology constraints while preserving logical semantics.
"""

from typing import Tuple, List, Dict, Optional
import copy
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRef
from src.module5.physical_ir.model import (
    PhysicalCircuitIR,
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    ExecutionProvenance,
    SCHEMA_VERSION,
)
from src.module5.physicalization.mapper import InitialMapper
from src.module5.physicalization.router import ShortestPathRouter
from src.module5.physicalization.trace import RoutingEvent, RoutingTrace
from src.module5.physicalization.verifier import SemanticPreservationVerifier


class PhysicalizationEngine:
    """Primary Stage 3 Physicalization Engine."""

    @classmethod
    def physicalize(
        cls,
        logical_circuit: QuantumCircuitIR,
        topology: DeviceTopology,
        initial_mapping: Optional[QubitMapping] = None,
    ) -> Tuple[PhysicalCircuitIR, RoutingTrace]:
        """
        Transforms a QuantumCircuitIR into a topology-compatible PhysicalCircuitIR.
        
        Guarantees:
        1. Input logical circuit is never mutated.
        2. Initial mapping is injective and deterministic.
        3. All two-qubit operations satisfy device topology constraints.
        4. Explicit physical SWAP operations are inserted for non-adjacent operations.
        5. Upstream provenance is preserved.
        """
        # Snapshot input hash for immutability check
        input_snapshot_hash = hash(str(logical_circuit))

        # Allocate / validate initial mapping M_0
        mapping_t0 = InitialMapper.allocate(logical_circuit, topology, custom_mapping=initial_mapping)

        # Working mapping copy M_t
        mapping_t = QubitMapping()
        for ref, node in mapping_t0.mapping.items():
            mapping_t.set_mapping(ref, node)

        physical_gates: List[PhysicalGateOperation] = []
        op_counter = 0
        trace = RoutingTrace(source_logical_circuit_id=logical_circuit.circuit_id)

        # Process each logical gate operation in logical_circuit
        for g_idx, gate_op in enumerate(logical_circuit.gates):
            g_name = gate_op.gate_type.value if hasattr(gate_op.gate_type, "value") else str(gate_op.gate_type)
            g_name = g_name.upper()

            q_target = gate_op.target_qubit
            q_controls = gate_op.control_qubits

            # Physicalize single-qubit gates
            if not q_controls:
                p_target = mapping_t.get_physical(q_target)

                pgate = PhysicalGateOperation(
                    gate_type=g_name,
                    target_node=p_target,
                    control_nodes=(),
                    operation_index=op_counter,
                )
                physical_gates.append(pgate)

                event = RoutingEvent(
                    operation_index=g_idx,
                    gate_type=g_name,
                    logical_operands=(q_target.to_string(),),
                    physical_operands_before=(p_target,),
                    routing_required=False,
                    selected_path=(p_target,),
                    inserted_swaps=[],
                    physical_operands_after=(p_target,),
                    mapping_after={r.to_string(): n for r, n in mapping_t.mapping.items()},
                )
                trace.add_event(event)
                op_counter += 1

            # Physicalize two-qubit gates
            elif len(q_controls) == 1:
                q_control = q_controls[0]

                p_control_before = mapping_t.get_physical(q_control)
                p_target_before = mapping_t.get_physical(q_target)

                if topology.is_connected(p_control_before, p_target_before):
                    # Directly realizable
                    pgate = PhysicalGateOperation(
                        gate_type=g_name,
                        control_nodes=(p_control_before,),
                        target_node=p_target_before,
                        operation_index=op_counter,
                    )
                    physical_gates.append(pgate)

                    event = RoutingEvent(
                        operation_index=g_idx,
                        gate_type=g_name,
                        logical_operands=(q_control.to_string(), q_target.to_string()),
                        physical_operands_before=(p_control_before, p_target_before),
                        routing_required=False,
                        selected_path=(p_control_before, p_target_before),
                        inserted_swaps=[],
                        physical_operands_after=(p_control_before, p_target_before),
                        mapping_after={r.to_string(): n for r, n in mapping_t.mapping.items()},
                    )
                    trace.add_event(event)
                    op_counter += 1
                else:
                    # Routing required! Insert SWAP operations
                    inserted_swaps, path, (p_control_after, p_target_after) = ShortestPathRouter.route_operation(
                        p_control_before, p_target_before, topology, mapping_t
                    )

                    # Emit physical SWAP operations
                    for swap_u, swap_v in inserted_swaps:
                        swap_gate = PhysicalGateOperation(
                            gate_type="SWAP",
                            control_nodes=(swap_u,),
                            target_node=swap_v,
                            operation_index=op_counter,
                        )
                        physical_gates.append(swap_gate)
                        op_counter += 1

                    # Emit routed two-qubit physical operation
                    pgate = PhysicalGateOperation(
                        gate_type=g_name,
                        control_nodes=(p_control_after,),
                        target_node=p_target_after,
                        operation_index=op_counter,
                    )
                    physical_gates.append(pgate)

                    event = RoutingEvent(
                        operation_index=g_idx,
                        gate_type=g_name,
                        logical_operands=(q_control.to_string(), q_target.to_string()),
                        physical_operands_before=(p_control_before, p_target_before),
                        routing_required=True,
                        selected_path=tuple(path),
                        inserted_swaps=inserted_swaps,
                        physical_operands_after=(p_control_after, p_target_after),
                        mapping_after={r.to_string(): n for r, n in mapping_t.mapping.items()},
                    )
                    trace.add_event(event)
                    op_counter += 1

            # Multi-qubit gates (e.g. TOFFOLI)
            else:
                p_controls = tuple(mapping_t.get_physical(q) for q in q_controls)
                p_target = mapping_t.get_physical(q_target)

                pgate = PhysicalGateOperation(
                    gate_type=g_name,
                    control_nodes=p_controls,
                    target_node=p_target,
                    operation_index=op_counter,
                )
                physical_gates.append(pgate)

                event = RoutingEvent(
                    operation_index=g_idx,
                    gate_type=g_name,
                    logical_operands=tuple(q.to_string() for q in q_controls) + (q_target.to_string(),),
                    physical_operands_before=p_controls + (p_target,),
                    routing_required=False,
                    selected_path=p_controls + (p_target,),
                    inserted_swaps=[],
                    physical_operands_after=p_controls + (p_target,),
                    mapping_after={r.to_string(): n for r, n in mapping_t.mapping.items()},
                )
                trace.add_event(event)
                op_counter += 1

        # Physical qubits set from topology nodes
        physical_qubits = [PhysicalQubit(node_id=n) for n in sorted(list(topology.nodes))]

        # Provenance propagation
        rutm_hash = logical_circuit.provenance.source_rutm_program_hash if logical_circuit.provenance else "rutm_hash_unknown"
        qtm_id = logical_circuit.provenance.source_qtm_machine_id if logical_circuit.provenance else "qtm_id_unknown"

        provenance = ExecutionProvenance(
            source_rutm_program_hash=rutm_hash,
            source_qtm_machine_id=qtm_id,
            logical_circuit_id=logical_circuit.circuit_id,
            physical_circuit_id=f"phys_{logical_circuit.circuit_id}",
            backend_id="STAGE_3_PHYSICALIZATION_AND_SWAP_ROUTING",
            compiler_version="0.5.0-alpha",
        )

        physical_circuit = PhysicalCircuitIR(
            physical_circuit_id=f"phys_{logical_circuit.circuit_id}",
            source_logical_circuit_id=logical_circuit.circuit_id,
            physical_qubits=physical_qubits,
            gates=physical_gates,
            mapping=mapping_t,
            topology=topology,
            provenance=provenance,
            schema_version=SCHEMA_VERSION,
        )

        # Verification
        ver_res = SemanticPreservationVerifier.verify(
            input_circuit=logical_circuit,
            input_circuit_snapshot_hash=input_snapshot_hash,
            physical_circuit=physical_circuit,
            final_mapping=mapping_t,
            topology=topology,
            trace=trace,
        )

        if not ver_res.verified:
            raise ValueError(f"Stage 3 Physicalization Engine verification failed: {ver_res.errors}")

        return (physical_circuit, trace)
