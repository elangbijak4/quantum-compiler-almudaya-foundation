"""
Module 5 Backend Abstraction Package — Capability Models, Validators, Compatibility Evaluators, and Serializers.
"""

from src.module5.backend.model import (
    BackendType,
    BackendIdentity,
    QubitCapacity,
    BackendTopologyCapability,
    GateCapability,
    GateConstraint,
    MeasurementCapability,
    ExecutionCapability,
    NumericalCapability,
    BackendCapabilityProvenance,
    BackendCapabilityModel,
    BACKEND_CAPABILITY_SCHEMA_VERSION,
)
from src.module5.backend.validator import (
    CapabilityValidationResult,
    validate_backend_capabilities,
)
from src.module5.backend.compatibility import (
    BackendCompatibilityResult,
    validate_backend_compatibility,
)
from src.module5.backend.serialization import (
    serialize_backend_capabilities,
    deserialize_backend_capabilities,
)
from src.module5.backend.reference import (
    create_reference_simulator_capabilities,
)

__all__ = [
    "BackendType",
    "BackendIdentity",
    "QubitCapacity",
    "BackendTopologyCapability",
    "GateCapability",
    "GateConstraint",
    "MeasurementCapability",
    "ExecutionCapability",
    "NumericalCapability",
    "BackendCapabilityProvenance",
    "BackendCapabilityModel",
    "BACKEND_CAPABILITY_SCHEMA_VERSION",
    "CapabilityValidationResult",
    "validate_backend_capabilities",
    "BackendCompatibilityResult",
    "validate_backend_compatibility",
    "serialize_backend_capabilities",
    "deserialize_backend_capabilities",
    "create_reference_simulator_capabilities",
]
