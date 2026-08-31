"""
Module 7 — Quantum Backend & Execution Domain Protocol Contracts & Stub Declarations.

Defines protocol interfaces for backend registries, lowering engines, reference simulators,
cloud adapters, and statistical result verifiers.
"""

from typing import Protocol, Dict, Any, Optional, List, Tuple
from src.module7.model import (
    BackendCapabilityModel,
    LoweringResult,
    ExecutionJobResult,
    ExecutionLifecycleStatus,
)


class BackendRegistryProtocol(Protocol):
    """Protocol for provider-neutral backend registry and capability discovery."""
    def register_backend(self, capability: BackendCapabilityModel) -> None:
        ...

    def get_backend(self, backend_id: str) -> Optional[BackendCapabilityModel]:
        ...

    def list_backends(self) -> Tuple[BackendCapabilityModel, ...]:
        ...


class LoweringEngineProtocol(Protocol):
    """Protocol for logical-to-native circuit lowering and topology mapping."""
    def lower_logical_circuit(
        self,
        logical_circuit: Any,
        capability: BackendCapabilityModel,
    ) -> LoweringResult:
        ...


class ReferenceSimulatorProtocol(Protocol):
    """Protocol for local virtual reference simulator execution runtime (Local First Policy)."""
    def execute_reference(
        self,
        lowered_result: LoweringResult,
        shots: int,
    ) -> ExecutionJobResult:
        ...


class ResultVerifierProtocol(Protocol):
    """Protocol for statistical execution result verification."""
    def verify_results(
        self,
        reference_job: ExecutionJobResult,
        observed_job: ExecutionJobResult,
        alpha_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        ...
