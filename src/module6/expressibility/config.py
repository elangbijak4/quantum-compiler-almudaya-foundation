"""
Module 6 Stage 2 — Expressibility Experiment Configuration Model.

Defines reproducible, serializable experiment configuration parameters for Stage 2.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib


@dataclass(frozen=True)
class ExpressibilityExperimentConfig:
    """
    Immutable experiment configuration for Stage 2 expressibility analysis.
    """
    experiment_id: str = "exp_stage2_default"
    algorithm_family_ids: Tuple[str, ...] = (
        "identity_family",
        "bit_flip_family",
        "two_state_cycle_family",
        "multi_state_cycle_family",
        "controlled_transition_family",
        "reversible_permutation_family",
    )
    sample_limits: Dict[str, int] = field(default_factory=lambda: {"default": 3})
    target_family_ids: Tuple[str, ...] = ("default_targets",)
    qubit_bounds: Tuple[int, int] = (1, 4)
    maximum_circuit_depth: int = 50
    parameter_values: Dict[str, Any] = field(default_factory=dict)
    primitive_vocabulary: Tuple[str, ...] = ("X", "CNOT", "TOFFOLI")
    epsilon: float = 1e-12
    equivalence_policy: str = "OPERATOR_SEMANTIC"
    global_phase_mode: str = "GLOBAL_PHASE_EQUIVALENT"

    def compute_config_hash(self) -> str:
        """Computes deterministic hash of experiment configuration."""
        data = {
            "experiment_id": self.experiment_id,
            "algorithm_family_ids": list(self.algorithm_family_ids),
            "sample_limits": self.sample_limits,
            "target_family_ids": list(self.target_family_ids),
            "qubit_bounds": list(self.qubit_bounds),
            "maximum_circuit_depth": self.maximum_circuit_depth,
            "parameter_values": self.parameter_values,
            "primitive_vocabulary": list(self.primitive_vocabulary),
            "epsilon": f"{self.epsilon:.12e}",
            "equivalence_policy": self.equivalence_policy,
            "global_phase_mode": self.global_phase_mode,
        }
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()
