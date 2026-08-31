"""
Module 6 Stage 6 — Session Lifecycle Manager.

Manages session lifecycle (CREATE_SESSION, SELECT_BASELINE, RESET_BASELINE, END_SESSION)
without mutating current evolutionary state GE(k).
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json
import uuid

from src.module6.evolution.state import EvolutionaryVocabularyState
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.resolver import EffectiveVocabularyResolver


class SessionLifecycle:
    """
    Manages active compilation session baseline states.
    
    Invariant: No session operation (create, override, reset, terminate) may mutate GE(k).
    """

    def __init__(self, evolution_state: EvolutionaryVocabularyState) -> None:
        self._evolution_state = evolution_state
        self._ge_hash_before = evolution_state.vocabulary_hash
        self._active_session: Optional[SessionBaseline] = None

    @property
    def evolution_state(self) -> EvolutionaryVocabularyState:
        return self._evolution_state

    @property
    def active_session(self) -> Optional[SessionBaseline]:
        return self._active_session

    def create_session(self, session_id: Optional[str] = None) -> SessionBaseline:
        """
        Creates a new session defaulting to current evolutionary state GE(k).
        """
        self._verify_evolution_immutability()
        sid = session_id if session_id is not None else f"session_{uuid.uuid4().hex[:8]}"
        gates = self._evolution_state.vocabulary
        b_hash = hashlib.sha256(json.dumps(gates).encode("utf-8")).hexdigest()

        session = SessionBaseline(
            session_id=sid,
            selected_gates=gates,
            baseline_hash=b_hash,
            source_evolution_stage=self._evolution_state.evolution_stage_id,
            source_vocabulary_hash=self._evolution_state.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
            provenance={"created_by": "SessionLifecycle", "stage": self._evolution_state.evolution_stage_id},
        )
        self._active_session = session
        self._verify_evolution_immutability()
        return session

    def select_user_baseline(
        self,
        user_gates: Tuple[str, ...],
        session_id: Optional[str] = None,
    ) -> SessionBaseline:
        """
        Sets a user-selected baseline Bu subseteq GE(k).
        """
        self._verify_evolution_immutability()
        sid = session_id if session_id is not None else (
            self._active_session.session_id if self._active_session else f"session_{uuid.uuid4().hex[:8]}"
        )

        sorted_gates = tuple(sorted(set(user_gates)))
        # Verify subset constraint Bu subseteq GE(k)
        invalid = set(sorted_gates) - set(self._evolution_state.vocabulary)
        if invalid:
            raise ValueError(
                f"INVALID_SESSION_BASELINE: Gates {sorted(invalid)} are outside evolutionary state GE(k)."
            )

        b_hash = hashlib.sha256(json.dumps(sorted_gates).encode("utf-8")).hexdigest()

        session = SessionBaseline(
            session_id=sid,
            selected_gates=sorted_gates,
            baseline_hash=b_hash,
            source_evolution_stage=self._evolution_state.evolution_stage_id,
            source_vocabulary_hash=self._evolution_state.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
            provenance={"user_override": True, "stage": self._evolution_state.evolution_stage_id},
        )
        self._active_session = session
        self._verify_evolution_immutability()
        return session

    def reset_baseline(self) -> SessionBaseline:
        """
        Resets session baseline to default evolutionary state GE(k).
        """
        self._verify_evolution_immutability()
        sid = self._active_session.session_id if self._active_session else f"session_{uuid.uuid4().hex[:8]}"
        gates = self._evolution_state.vocabulary
        b_hash = hashlib.sha256(json.dumps(gates).encode("utf-8")).hexdigest()

        session = SessionBaseline(
            session_id=sid,
            selected_gates=gates,
            baseline_hash=b_hash,
            source_evolution_stage=self._evolution_state.evolution_stage_id,
            source_vocabulary_hash=self._evolution_state.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
            provenance={"reset": True, "stage": self._evolution_state.evolution_stage_id},
        )
        self._active_session = session
        self._verify_evolution_immutability()
        return session

    def end_session(self) -> None:
        """
        Ends active session. Restores default evolutionary context.
        """
        self._verify_evolution_immutability()
        self._active_session = None
        self._verify_evolution_immutability()

    def get_effective_vocabulary(self) -> Tuple[str, ...]:
        """
        Resolves G_effective for current active session.
        """
        self._verify_evolution_immutability()
        if self._active_session is None:
            return self._evolution_state.vocabulary
        return EffectiveVocabularyResolver.resolve_effective_vocabulary(
            self._evolution_state, self._active_session
        )

    def _verify_evolution_immutability(self) -> None:
        """Verifies GE(k) hash was not mutated."""
        if self._evolution_state.vocabulary_hash != self._ge_hash_before:
            raise RuntimeError("EVOLUTION_STATE_MUTATION_DETECTED: GE(k) hash changed during session operation.")
