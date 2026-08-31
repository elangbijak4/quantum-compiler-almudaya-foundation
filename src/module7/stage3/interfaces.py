"""
Module 7 Stage 3 — Reference Simulator Protocols & Interfaces.

Defines standard protocols for local virtual quantum reference simulator runtimes.
"""

from typing import Protocol, Dict, Any, Optional
from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import LoweringResultArtifact
from src.module7.stage3.model import (
    SimulatorConfig,
    SimulatorJobResult,
)


class ReferenceSimulatorProtocol(Protocol):
    """Protocol for Module 7 Stage 3 Local Virtual Reference Quantum Simulator."""

    def execute_lowered_circuit(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
        config: SimulatorConfig,
    ) -> SimulatorJobResult:
        """Executes a semantically verified lowered native circuit on local reference simulator."""
        ...
