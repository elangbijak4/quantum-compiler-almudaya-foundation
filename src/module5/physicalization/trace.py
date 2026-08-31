"""
Module 5 Stage 3 — Auditable Routing Trace Models.

Defines RoutingEvent and RoutingTrace for deterministic physicalization auditing.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import json


@dataclass
class RoutingEvent:
    """Audit record for a single logical gate physicalization/routing event."""
    operation_index: int
    gate_type: str
    logical_operands: Tuple[str, ...]
    physical_operands_before: Tuple[int, ...]
    routing_required: bool
    selected_path: Tuple[int, ...]
    inserted_swaps: List[Tuple[int, int]]
    physical_operands_after: Tuple[int, ...]
    mapping_after: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_index": self.operation_index,
            "gate_type": self.gate_type,
            "logical_operands": list(self.logical_operands),
            "physical_operands_before": list(self.physical_operands_before),
            "routing_required": self.routing_required,
            "selected_path": list(self.selected_path),
            "inserted_swaps": [list(sw) for sw in self.inserted_swaps],
            "physical_operands_after": list(self.physical_operands_after),
            "mapping_after": self.mapping_after,
        }


@dataclass
class RoutingTrace:
    """Complete auditable routing trace for a physicalized circuit."""
    source_logical_circuit_id: str
    events: List[RoutingEvent] = field(default_factory=list)

    def add_event(self, event: RoutingEvent) -> None:
        self.events.append(event)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_logical_circuit_id": self.source_logical_circuit_id,
            "total_events": len(self.events),
            "total_swaps_inserted": sum(len(e.inserted_swaps) for e in self.events),
            "events": [e.to_dict() for e in self.events],
        }

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
