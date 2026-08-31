"""
Module 6 Stage 6 — Governed Vocabulary Promotion.

Defines PromotionRecord and PromotionAuthorizationStatus for explicit, auditable gate promotions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class PromotionAuthorizationStatus(str, Enum):
    """Authorization status for gate promotion into production evolutionary vocabulary."""
    EXPLICITLY_AUTHORIZED = "EXPLICITLY_AUTHORIZED"
    PENDING_AUTHORIZATION = "PENDING_AUTHORIZATION"
    REJECTED = "REJECTED"
    UNAUTHORIZED_AUTOMATIC = "UNAUTHORIZED_AUTOMATIC"


@dataclass(frozen=True)
class PromotionRecord:
    """
    Immutable audit record for a governed vocabulary promotion event.
    
    A candidate gate MUST be explicitly authorized with an auditable PromotionRecord
    before it can transition from CandidateVocabulary into EvolutionaryVocabularyState GE(k+1).
    """
    promotion_id: str
    parent_evolution_stage: str
    candidate_gate_ids: Tuple[str, ...]
    candidate_hashes: Tuple[str, ...]
    evidence_reference: str
    equivalence_reference: str
    authorization_status: PromotionAuthorizationStatus
    authorized_by: str
    promotion_timestamp: str
    resulting_vocabulary_hash: str
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        return {
            "promotion_id": self.promotion_id,
            "parent_evolution_stage": self.parent_evolution_stage,
            "candidate_gate_ids": list(self.candidate_gate_ids),
            "candidate_hashes": list(self.candidate_hashes),
            "evidence_reference": self.evidence_reference,
            "equivalence_reference": self.equivalence_reference,
            "authorization_status": self.authorization_status.value,
            "authorized_by": self.authorized_by,
            "promotion_timestamp": self.promotion_timestamp,
            "resulting_vocabulary_hash": self.resulting_vocabulary_hash,
            "provenance": dict(self.provenance),
        }
