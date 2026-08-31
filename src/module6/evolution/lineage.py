"""
Module 6 Stage 6 — Evolutionary Lineage Manager.

Manages compiler vocabulary lineage G0 -> G1 -> G2 ..., enforcing monotonic growth
and cryptographically audited state transitions.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json
import datetime

from src.module6.evolution.state import EvolutionaryVocabularyState, create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus


class EvolutionaryLineageManager:
    """
    Manages evolutionary vocabulary state transitions.
    
    Enforces:
    1. Monotonicity: GE(k) subseteq GE(k+1)
    2. Governed Promotion: Candidates require explicit PromotionAuthorizationStatus.EXPLICITLY_AUTHORIZED
    3. Reproducible parent/child hashes
    """

    def __init__(self, initial_state: Optional[EvolutionaryVocabularyState] = None) -> None:
        self._current_state = initial_state if initial_state is not None else create_initial_evolutionary_state()
        self._history: Dict[str, EvolutionaryVocabularyState] = {
            self._current_state.evolution_stage_id: self._current_state
        }

    @property
    def current_state(self) -> EvolutionaryVocabularyState:
        """Gets current evolutionary state GE(k)."""
        return self._current_state

    def get_state(self, stage_id: str) -> Optional[EvolutionaryVocabularyState]:
        """Retrieves a historical evolutionary state by ID."""
        return self._history.get(stage_id)

    def promote_candidates(
        self,
        promotion_record: PromotionRecord,
        candidate_gate_names: Tuple[str, ...],
    ) -> EvolutionaryVocabularyState:
        """
        Executes explicit, governed promotion of candidate gates into new state GE(k+1).
        
        Raises ValueError if authorization_status is not EXPLICITLY_AUTHORIZED.
        """
        if promotion_record.authorization_status != PromotionAuthorizationStatus.EXPLICITLY_AUTHORIZED:
            raise ValueError(
                f"UNAUTHORIZED_PROMOTION: Cannot promote candidate gates with status {promotion_record.authorization_status}."
            )

        parent = self._current_state
        # Monotonic union: GE(k+1) = GE(k) U candidate_gate_names
        new_vocab = tuple(sorted(set(parent.vocabulary).union(candidate_gate_names)))
        new_vocab_hash = hashlib.sha256(json.dumps(new_vocab).encode("utf-8")).hexdigest()

        # Verify monotonicity invariant GE(k) subseteq GE(k+1)
        if not set(parent.vocabulary).issubset(set(new_vocab)):
            raise ValueError("MONOTONICITY_VIOLATION: New evolutionary vocabulary lost baseline gates.")

        next_stage_num = len(self._history)
        next_stage_id = f"GE_{next_stage_num}"

        new_state = EvolutionaryVocabularyState(
            evolution_stage_id=next_stage_id,
            parent_stage_id=parent.evolution_stage_id,
            vocabulary=new_vocab,
            parent_vocabulary_hash=parent.vocabulary_hash,
            vocabulary_hash=new_vocab_hash,
            promoted_gates=tuple(sorted(set(candidate_gate_names))),
            promotion_records=parent.promotion_records + (promotion_record,),
            provenance={
                "promotion_id": promotion_record.promotion_id,
                "authorized_by": promotion_record.authorized_by,
                "timestamp": promotion_record.promotion_timestamp,
            },
            compiler_version=parent.compiler_version,
        )

        self._history[next_stage_id] = new_state
        self._current_state = new_state
        return new_state
