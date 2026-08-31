"""
Module 7 Stage 2 — Qubit Mapping & Topology Routing Engine.

Provides deterministic logical-to-physical qubit mapping and topology-constrained
SWAP insertion routing algorithms.
"""

from typing import Dict, List, Tuple, Set, Optional, Any
from src.module7.model import BackendCapabilityModel


class DeterministicTopologyRouter:
    """
    Deterministic Topology Router and Qubit Mapper.
    
    Invariants:
    1. Deterministic initial mapping (logical qubit i -> physical qubit i).
    2. Enforces backend.topology_coupling_map constraints.
    3. Deterministic SWAP insertion routing for non-adjacent physical qubits.
    4. Tracks inserted SWAP operations and mapping transitions in provenance.
    """

    def __init__(self, backend_capability: BackendCapabilityModel) -> None:
        self.backend = backend_capability
        self.coupling_map: Set[Tuple[int, int]] = set(backend_capability.topology_coupling_map)
        # Bidirectional graph adjacency for routing paths
        self.adjacency: Dict[int, Set[int]] = {i: set() for i in range(backend_capability.qubit_count)}
        for q1, q2 in backend_capability.topology_coupling_map:
            self.adjacency[q1].add(q2)
            self.adjacency[q2].add(q1)

    def generate_initial_mapping(self, logical_qubits: List[int]) -> Dict[int, int]:
        """
        Generates initial deterministic mapping (logical q_i -> physical q_i).
        Raises ValueError if logical qubits exceed physical device capacity.
        """
        max_logical = max(logical_qubits) if logical_qubits else 0
        if max_logical >= self.backend.qubit_count or len(set(logical_qubits)) > self.backend.qubit_count:
            raise ValueError(
                f"BACKEND_CAPABILITY_MISMATCH: Logical qubits exceed physical backend capacity "
                f"(required {max_logical + 1}, available {self.backend.qubit_count})."
            )
        mapping: Dict[int, int] = {q: q for q in sorted(set(logical_qubits))}
        return mapping

    def find_shortest_path(self, start: int, target: int) -> List[int]:
        """Finds shortest path between physical qubits using deterministic BFS."""
        if start == target:
            return [start]
        queue: List[List[int]] = [[start]]
        visited: Set[int] = {start}

        while queue:
            path = queue.pop(0)
            node = path[-1]
            for neighbor in sorted(self.adjacency.get(node, set())):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def route_gate_sequence(
        self,
        gate_sequence: Tuple[Dict[str, Any], ...],
        initial_mapping: Dict[int, int],
    ) -> Tuple[Tuple[Dict[str, Any], ...], Dict[int, int], int]:
        """
        Routes native gate sequence to satisfy physical coupling map constraints.
        Inserts deterministic SWAP operations when physical qubits are not adjacent.
        
        Returns:
            (routed_gate_sequence, final_qubit_mapping, inserted_swap_count)
        """
        current_mapping = dict(initial_mapping)
        routed_gates: List[Dict[str, Any]] = []
        inserted_swap_count = 0

        for gate_info in gate_sequence:
            gate_name = gate_info["gate"]
            logical_qubits = gate_info["qubits"]
            params = gate_info.get("params", {})

            if len(logical_qubits) <= 1:
                phys_qubits = tuple(current_mapping[q] for q in logical_qubits)
                routed_gates.append({
                    "gate": gate_name,
                    "qubits": phys_qubits,
                    "params": params,
                    "source_logical": gate_info.get("source_logical", gate_name),
                    "is_routing_swap": False,
                })
                continue

            if len(logical_qubits) == 2:
                q1_log, q2_log = logical_qubits
                p1, p2 = current_mapping[q1_log], current_mapping[q2_log]

                if (p1, p2) in self.coupling_map or (p2, p1) in self.coupling_map or not self.coupling_map:
                    routed_gates.append({
                        "gate": gate_name,
                        "qubits": (p1, p2),
                        "params": params,
                        "source_logical": gate_info.get("source_logical", gate_name),
                        "is_routing_swap": False,
                    })
                else:
                    # Non-adjacent: find shortest path and insert SWAP gates along path
                    path = self.find_shortest_path(p1, p2)
                    if not path or len(path) < 2:
                        raise ValueError(f"TOPOLOGY_FAILURE: No routing path between physical qubits {p1} and {p2}.")

                    # Insert SWAP operations to bring p1 adjacent to p2
                    for i in range(len(path) - 2):
                        swap_p1, swap_p2 = path[i], path[i + 1]
                        routed_gates.append({
                            "gate": "SWAP",
                            "qubits": (swap_p1, swap_p2),
                            "params": {},
                            "source_logical": "ROUTING_SWAP",
                            "is_routing_swap": True,
                        })
                        inserted_swap_count += 1
                        # Update mapping reverse lookup
                        for l_q, p_q in list(current_mapping.items()):
                            if p_q == swap_p1:
                                current_mapping[l_q] = swap_p2
                            elif p_q == swap_p2:
                                current_mapping[l_q] = swap_p1

                    # Execute 2-qubit gate on adjacent physical qubits
                    final_p1 = current_mapping[q1_log]
                    final_p2 = current_mapping[q2_log]
                    routed_gates.append({
                        "gate": gate_name,
                        "qubits": (final_p1, final_p2),
                        "params": params,
                        "source_logical": gate_info.get("source_logical", gate_name),
                        "is_routing_swap": False,
                    })

        return tuple(routed_gates), current_mapping, inserted_swap_count
