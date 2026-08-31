"""
Module 6 Stage 7 — Resolution Validator.

Validates requested user baselines, backend constraints, required/forbidden gates, and session snapshots.
"""

from typing import Tuple, List, Dict, Any, Optional
from src.module6.evolution.state import EvolutionaryVocabularyState
from src.module6.session.baseline import SessionBaseline
from src.module6.resolution.model import ConfigurationStatus, ResolutionConflict


class ResolutionValidator:
    """
    Validates requested configurations prior to EffectiveCompilationContext construction.
    """

    @classmethod
    def validate_user_baseline(
        cls,
        evolution_state: EvolutionaryVocabularyState,
        requested_gates: Tuple[str, ...],
        compilation_constraints: Optional[Dict[str, Any]] = None,
        backend_constraints: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ConfigurationStatus, Tuple[ResolutionConflict, ...]]:
        """
        Validates user baseline subset constraint Bu subseteq GE(k), user constraints, and backend constraints.
        """
        conflicts: List[ResolutionConflict] = []

        # Rule 1: Empty baseline is prohibited
        if not requested_gates:
            conflict = ResolutionConflict(
                conflict_id="ERR_EMPTY_VOCAB",
                conflict_type="EMPTY_VOCABULARY",
                description="User requested an empty gate vocabulary.",
                competing_sources=("UserBaseline",),
                resolution_action="REJECT_EMPTY_VOCABULARY",
            )
            return ConfigurationStatus.INVALID_CONFIGURATION, (conflict,)

        ge_set = set(evolution_state.vocabulary)
        req_set = set(requested_gates)

        # Rule 2: Baseline outside GE(k)
        invalid_gates = req_set - ge_set
        if invalid_gates:
            conflict = ResolutionConflict(
                conflict_id="ERR_UNAVAILABLE_GATE",
                conflict_type="GATE_OUTSIDE_EVOLUTIONARY_STATE",
                description=f"Gates {sorted(invalid_gates)} outside GE(k).",
                competing_sources=("UserBaseline", "EvolutionaryState"),
                resolution_action="REJECT_UNAVAILABLE_GATES",
            )
            conflicts.append(conflict)
            return ConfigurationStatus.INVALID_CONFIGURATION, tuple(conflicts)

        # Check resulting effective set after applying forbidden / backend restrictions
        eff_set = set(req_set)
        if compilation_constraints:
            req_required = set(compilation_constraints.get("required_gates", []))
            req_forbidden = set(compilation_constraints.get("forbidden_gates", []))

            # Required gate unavailable in GE(k) or excluded by requested baseline
            unavail_req = req_required - req_set
            if unavail_req:
                conflicts.append(
                    ResolutionConflict(
                        conflict_id="ERR_REQUIRED_GATE_UNAVAILABLE",
                        conflict_type="REQUIRED_GATE_UNAVAILABLE",
                        description=f"Required gates {sorted(unavail_req)} not in effective baseline.",
                        competing_sources=("CompilationConstraints", "EffectiveBaseline"),
                        resolution_action="REJECT_REQUIRED_GATE_UNAVAILABLE",
                    )
                )

            # Forbidden gate requested in baseline
            forbid_conflict = req_set & req_forbidden
            if forbid_conflict:
                conflicts.append(
                    ResolutionConflict(
                        conflict_id="ERR_FORBIDDEN_GATE_REQUESTED",
                        conflict_type="FORBIDDEN_GATE_REQUESTED",
                        description=f"Requested gates {sorted(forbid_conflict)} are forbidden by constraints.",
                        competing_sources=("UserBaseline", "CompilationConstraints"),
                        resolution_action="EXCLUDE_FORBIDDEN_GATES",
                    )
                )
                eff_set -= req_forbidden

        if backend_constraints:
            backend_supported = set(backend_constraints.get("supported_gates", ge_set))
            disallowed_by_backend = req_set - backend_supported
            if disallowed_by_backend:
                conflicts.append(
                    ResolutionConflict(
                        conflict_id="ERR_BACKEND_CONFLICT",
                        conflict_type="BACKEND_CONFLICT",
                        description=f"Gates {sorted(disallowed_by_backend)} not supported by target backend.",
                        competing_sources=("UserBaseline", "BackendConstraints"),
                        resolution_action="RESTRICT_TO_BACKEND_CAPABILITY",
                    )
                )
                eff_set &= backend_supported

        # If restrictions resulted in an empty effective set, configuration is INVALID
        if not eff_set:
            conflicts.append(
                ResolutionConflict(
                    conflict_id="ERR_EMPTY_EFFECTIVE_VOCAB",
                    conflict_type="EMPTY_EFFECTIVE_VOCABULARY",
                    description="Constraints resulted in an empty effective gate vocabulary.",
                    competing_sources=("Constraints", "EffectiveBaseline"),
                    resolution_action="REJECT_EMPTY_EFFECTIVE_VOCABULARY",
                )
            )
            return ConfigurationStatus.INVALID_CONFIGURATION, tuple(conflicts)

        if any(c.conflict_type in ("GATE_OUTSIDE_EVOLUTIONARY_STATE", "REQUIRED_GATE_UNAVAILABLE", "EMPTY_EFFECTIVE_VOCABULARY") for c in conflicts):
            return ConfigurationStatus.INVALID_CONFIGURATION, tuple(conflicts)

        if conflicts:
            return ConfigurationStatus.CONFIGURATION_CONFLICT, tuple(conflicts)

        return ConfigurationStatus.VALID_CONFIGURATION, ()
