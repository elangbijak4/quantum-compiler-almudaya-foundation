"""
Module 5 Stage 3 Physicalization Package — Initial Mapping, SWAP Routing, Verifier, and Tracing.
"""

from src.module5.physicalization.mapper import InitialMapper
from src.module5.physicalization.router import ShortestPathRouter
from src.module5.physicalization.trace import RoutingEvent, RoutingTrace
from src.module5.physicalization.verifier import (
    PhysicalizationVerificationResult,
    SemanticPreservationVerifier,
)
from src.module5.physicalization.physicalizer import PhysicalizationEngine

__all__ = [
    "InitialMapper",
    "ShortestPathRouter",
    "RoutingEvent",
    "RoutingTrace",
    "PhysicalizationVerificationResult",
    "SemanticPreservationVerifier",
    "PhysicalizationEngine",
]
