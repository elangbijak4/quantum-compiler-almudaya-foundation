"""
Module 7 Stage 5 — Abstract Interface Definitions.

Defines protocol interfaces for statistical result verification, canonical probability
distribution construction, distance metric calculation, and Stage 11 lineage extension.
"""

from typing import Protocol, Dict, Any, Optional, Tuple
from src.module7.stage4.model import ProviderNeutralExecutionResult
from src.module7.stage5.model import (
    StatisticalVerificationPolicy,
    StatisticalVerificationRecord,
    StatisticalVerificationDecision,
)


class StatisticalVerifierProtocol(Protocol):
    """
    Protocol for statistical verification engine comparing observed distribution against reference.
    """

    def verify_result(
        self,
        observed_result: ProviderNeutralExecutionResult,
        reference_distribution: Dict[str, float],
        reference_id: str,
        policy: StatisticalVerificationPolicy,
    ) -> StatisticalVerificationRecord:
        """Evaluates statistical distance and returns immutable StatisticalVerificationRecord."""
        ...


class LineageExtensionProtocol(Protocol):
    """
    Protocol for appending Stage 5 statistical verification evidence to Module 6 Stage 11 repository.
    """

    def append_verification_event(
        self,
        verification_record: StatisticalVerificationRecord,
    ) -> str:
        """Appends verification record to historical lineage and returns event hash."""
        ...
