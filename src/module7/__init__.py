"""
Module 7 — Quantum Backend & Execution Domain Subpackage Exports.

Provides provider-neutral backend capability models, lowering interfaces, local reference simulator contracts,
historical backend registry engine, and result verification types.
"""

from src.module7.model import (
    ExecutionLifecycleStatus,
    ExecutionFailureCategory,
    CredentialReference,
    BackendCapabilityModel,
    LoweringResult,
    ExecutionJobResult,
)
from src.module7.interfaces import (
    BackendRegistryProtocol,
    LoweringEngineProtocol,
    ReferenceSimulatorProtocol,
    ResultVerifierProtocol,
)
from src.module7.registry import HistoricalBackendRegistry
from src.module7.serialization import (
    serialize_backend_capability_model,
    deserialize_backend_capability_model,
)

__all__ = [
    "ExecutionLifecycleStatus",
    "ExecutionFailureCategory",
    "CredentialReference",
    "BackendCapabilityModel",
    "LoweringResult",
    "ExecutionJobResult",
    "BackendRegistryProtocol",
    "LoweringEngineProtocol",
    "ReferenceSimulatorProtocol",
    "ResultVerifierProtocol",
    "HistoricalBackendRegistry",
    "serialize_backend_capability_model",
    "deserialize_backend_capability_model",
]
