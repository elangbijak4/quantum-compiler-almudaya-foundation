"""
Module 4 Circuit IR Package — Model, Validator, and Serialization.
"""

from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    QubitRef,
    GateOperation,
    AncillaDeclaration,
    CircuitProvenance,
    RegisterType,
    AncillaStatus,
    LogicalGateType,
    SCHEMA_VERSION,
)
from src.module4.circuit_ir.validator import (
    CircuitValidationResult,
    validate_circuit_ir,
)
from src.module4.circuit_ir.serialization import (
    serialize_circuit_ir_to_dict,
    serialize_circuit_ir_to_json,
    deserialize_circuit_ir_from_dict,
    deserialize_circuit_ir_from_json,
)

__all__ = [
    "QuantumCircuitIR",
    "QubitRegister",
    "QubitRef",
    "GateOperation",
    "AncillaDeclaration",
    "CircuitProvenance",
    "RegisterType",
    "AncillaStatus",
    "LogicalGateType",
    "SCHEMA_VERSION",
    "CircuitValidationResult",
    "validate_circuit_ir",
    "serialize_circuit_ir_to_dict",
    "serialize_circuit_ir_to_json",
    "deserialize_circuit_ir_from_dict",
    "deserialize_circuit_ir_from_json",
]
