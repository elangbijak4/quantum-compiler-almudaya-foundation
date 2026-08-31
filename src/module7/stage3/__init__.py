"""
Module 7 Stage 3 — Subpackage Exports.

Exposes local virtual reference simulator engine, statevector simulator,
shot sampler, configuration, models, and protocol definitions.
"""

from src.module7.stage3.model import (
    SimulationExecutionStatus,
    SimulatorConfig,
    ReferenceStatevectorSummary,
    SimulatorJobResult,
)
from src.module7.stage3.interfaces import ReferenceSimulatorProtocol
from src.module7.stage3.statevector import LocalReferenceStatevectorSimulator
from src.module7.stage3.sampling import DeterministicShotSampler
from src.module7.stage3.engine import LocalReferenceSimulatorEngine

__all__ = [
    "SimulationExecutionStatus",
    "SimulatorConfig",
    "ReferenceStatevectorSummary",
    "SimulatorJobResult",
    "ReferenceSimulatorProtocol",
    "LocalReferenceStatevectorSimulator",
    "DeterministicShotSampler",
    "LocalReferenceSimulatorEngine",
]
