"""
Module 5 Stage 3 — Deterministic Shortest-Path Topology Router.

Computes canonical shortest physical routing paths with deterministic lexicographical tie-breaking,
inserts explicit SWAP operations, and updates QubitMapping M_t dynamically.
"""

from typing import List, Tuple, Set, Dict, Optional
from collections import deque
from src.module5.physical_ir.model import QubitMapping, DeviceTopology


class ShortestPathRouter:
    """Deterministic BFS router for topology-constrained SWAP routing."""

    @staticmethod
    def find_shortest_path(u: int, v: int, topology: DeviceTopology) -> List[int]:
        """
        Finds the shortest physical path between node u and node v in topology.
        
        Tie-breaking policy:
          Among all paths of minimum length, returns the lexicographically smallest node sequence tuple.
        """
        if u not in topology.nodes:
            raise ValueError(f"Routing failure: Source physical node {u} does not exist in topology.")
        if v not in topology.nodes:
            raise ValueError(f"Routing failure: Target physical node {v} does not exist in topology.")

        if u == v:
            return [u]

        # BFS queue storing path tuples (node_sequence)
        queue: deque[Tuple[int, ...]] = deque([(u,)])
        visited: Dict[int, int] = {u: 1}  # node -> min path length
        shortest_paths: List[Tuple[int, ...]] = []
        min_length: Optional[int] = None

        # Build adjacency graph
        adj: Dict[int, List[int]] = {n: [] for n in topology.nodes}
        for n1, n2 in topology.edges:
            adj[n1].append(n2)
            adj[n2].append(n1)

        # Sort adjacency lists for deterministic traversal
        for n in adj:
            adj[n].sort()

        while queue:
            current_path = queue.popleft()
            curr_node = current_path[-1]
            path_len = len(current_path)

            if min_length is not None and path_len > min_length:
                break

            if curr_node == v:
                if min_length is None:
                    min_length = path_len
                if path_len == min_length:
                    shortest_paths.append(current_path)
                continue

            for neighbor in adj[curr_node]:
                if neighbor not in visited or visited[neighbor] == path_len + 1:
                    visited[neighbor] = path_len + 1
                    queue.append(current_path + (neighbor,))

        if not shortest_paths:
            raise ValueError(
                f"Routing failure: Disconnected topology with no routing path between physical node {u} and node {v}."
            )

        # Lexicographically smallest path sequence tie-breaker
        shortest_paths.sort()
        return list(shortest_paths[0])

    @classmethod
    def route_operation(
        cls,
        u_phys: int,
        v_phys: int,
        topology: DeviceTopology,
        mapping: QubitMapping,
    ) -> Tuple[List[Tuple[int, int]], List[int], Tuple[int, int]]:
        """
        Routes a 2-qubit operation between u_phys and v_phys.
        
        Returns:
          (inserted_swaps, path, (new_u_phys, new_v_phys))
          
        Updates mapping dynamically for each inserted SWAP operation.
        """
        if topology.is_connected(u_phys, v_phys):
            return ([], [u_phys, v_phys], (u_phys, v_phys))

        path = cls.find_shortest_path(u_phys, v_phys, topology)

        inserted_swaps: List[Tuple[int, int]] = []
        # SWAP along path: path[0] with path[1], path[1] with path[2], ..., path[-3] with path[-2]
        for i in range(len(path) - 2):
            swap_u = path[i]
            swap_v = path[i + 1]
            mapping.apply_swap(swap_u, swap_v)
            inserted_swaps.append((swap_u, swap_v))

        new_u_phys = path[-2]
        new_v_phys = path[-1]

        # Verify adjacency satisfied
        if not topology.is_connected(new_u_phys, new_v_phys):
            raise ValueError(
                f"Routing error: Post-swap physical nodes ({new_u_phys}, {new_v_phys}) are still disconnected in topology."
            )

        return (inserted_swaps, path, (new_u_phys, new_v_phys))
