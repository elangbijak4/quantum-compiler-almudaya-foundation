"""
Module 7 Stage 2 — Lowering Protocol & Interface Definitions.

Defines standard protocols for lowering engines, gate decomposition rules,
and semantic verification adapters.
"""

from typing import Protocol, Dict, Any, Optional
from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import (
    LoweringPolicy,
    LoweringResultArtifact,
    NativeCircuitArtifact,
)


class LoweringEngineProtocol(Protocol):
    """Protocol for Module 7 Stage 2 Lowering Engine."""

    def lower_circuit(
        self,
        logical_circuit_id: str,
        logical_circuit_hash: str,
        backend_capability: BackendCapabilityModel,
        policy: LoweringPolicy,
    ) -> LoweringResultArtifact:
        ...


class SemanticVerificationAdapterProtocol(Protocol):
    """Protocol for delegating native circuit verification to Module 4 Stage 4 semantic authority."""

    def verify_equivalence(
        self,
        logical_circuit_hash: str,
        native_circuit_hash: str,
    ) -> str:
        """Returns verification status string: 'VERIFIED', 'SEMANTICALLY_NON_EQUIVALENT', or 'INCONCLUSIVE'."""
        ...
