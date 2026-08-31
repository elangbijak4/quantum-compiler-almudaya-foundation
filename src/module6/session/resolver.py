"""
Module 6 Stage 6 — Effective Vocabulary Resolver.

Resolves effective gate vocabulary G_effective for a session, enforcing G_effective subseteq GE(k).
"""

from typing import Tuple, List, Set
from src.module6.evolution.state import EvolutionaryVocabularyState
from src.module6.session.baseline import SessionBaseline, BaselineMode


class EffectiveVocabularyResolver:
    """
    Resolves the effective gate vocabulary permitted during a compilation request.
    
    Rule:
    - If baseline_mode == DEFAULT_EVOLUTIONARY: G_effective = GE(k)
    - If baseline_mode == USER_SELECTED: G_effective = Bu subseteq GE(k)
    """

    @classmethod
    def resolve_effective_vocabulary(
        cls,
        evolution_state: EvolutionaryVocabularyState,
        session_baseline: SessionBaseline,
    ) -> Tuple[str, ...]:
        """
        Resolves G_effective as a sorted tuple of gate names.
        
        Raises ValueError if user-selected Bu is not a subset of GE(k).
        """
        ge_set = set(evolution_state.vocabulary)
        bu_set = set(session_baseline.selected_gates)

        # Enforce constraint Bu subseteq GE(k)
        invalid_gates = bu_set - ge_set
        if invalid_gates:
            raise ValueError(
                f"INVALID_SESSION_BASELINE: Selected gates {sorted(invalid_gates)} are outside current evolutionary state {evolution_state.evolution_stage_id} ({evolution_state.vocabulary})."
            )

        if session_baseline.baseline_mode == BaselineMode.DEFAULT_EVOLUTIONARY:
            return evolution_state.vocabulary
        else:
            return tuple(sorted(bu_set))
