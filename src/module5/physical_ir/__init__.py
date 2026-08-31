"""
Module 5 PhysicalCircuitIR Package — Models, Validators, and Serializers.
"""

from src.module5.physical_ir.model import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    SCHEMA_VERSION,
)
from src.module5.physical_ir.validator import (
    PhysicalCircuitValidationResult,
    validate_physical_circuit_ir,
)
from src.module5.physical_ir.serialization import (
    serialize_physical_circuit_ir,
    deserialize_physical_circuit_ir,
)

__all__ = [
    "PhysicalQubit",
    "QubitMapping",
    "DeviceTopology",
    "PhysicalGateOperation",
    "PhysicalCircuitIR",
    "ExecutionProvenance",
    "SCHEMA_VERSION",
    "PhysicalCircuitValidationResult",
    "validate_physical_circuit_ir",
    "serialize_physical_circuit_ir",
    "deserialize_physical_circuit_ir",
]
