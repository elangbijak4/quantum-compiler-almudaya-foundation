"""
Module 5 Stage 3 — Initial Logical-to-Physical Qubit Mapper.

Discovers logical qubits used in QuantumCircuitIR and constructs a deterministic, injective
initial QubitMapping M_0: Q_L -> Q_P onto physical device topology nodes.
"""

from typing import List, Set, Optional
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRef
from src.module5.physical_ir.model import QubitMapping, DeviceTopology, PhysicalQubit


class InitialMapper:
    """Deterministic initial logical-to-physical qubit allocator."""

    @staticmethod
    def discover_logical_qubits(circuit: QuantumCircuitIR) -> List[QubitRef]:
        """
        Discovers all logical qubit references declared in the QuantumCircuitIR registers.
        Order is canonical: sorted by register_id name, then register index.
        """
        refs: List[QubitRef] = []
        for reg in sorted(circuit.registers, key=lambda r: r.register_id):
            for i in range(reg.width):
                refs.append(reg.get_qubit_ref(i))
        return refs

    @classmethod
    def allocate(
        cls,
        circuit: QuantumCircuitIR,
        topology: DeviceTopology,
        custom_mapping: Optional[QubitMapping] = None,
    ) -> QubitMapping:
        """
        Constructs and validates the initial QubitMapping M_0.
        
        If custom_mapping is provided:
          Validates injectivity, capacity, and existence in topology.
        Else:
          Allocates canonically: q_i -> sorted(topology.nodes)[i].
        """
        logical_refs = cls.discover_logical_qubits(circuit)
        sorted_nodes = sorted(list(topology.nodes))

        if len(logical_refs) > len(sorted_nodes):
            raise ValueError(
                f"Physicalization rejection: Insufficient physical qubits in topology. Circuit requires {len(logical_refs)} logical qubits, topology provides {len(sorted_nodes)} physical nodes."
            )

        if custom_mapping is not None:
            # Validate custom mapping completeness and topology existence
            mapping = custom_mapping
            if not mapping.is_injective():
                raise ValueError("Physicalization rejection: Initial custom mapping is non-injective (qubit collision).")

            for ref in logical_refs:
                p_node = mapping.get_physical(ref)
                if p_node not in topology.nodes:
                    raise ValueError(
                        f"Physicalization rejection: Mapped physical node {p_node} for logical qubit {ref} does not exist in topology."
                    )
            return mapping

        # Canonical allocation: logical_refs[i] -> sorted_nodes[i]
        mapping = QubitMapping()
        for i, ref in enumerate(logical_refs):
            p_node = sorted_nodes[i]
            mapping.set_mapping(ref, p_node)

        if not mapping.is_injective():
            raise ValueError("Physicalization rejection: Constructed initial mapping is non-injective.")

        return mapping
