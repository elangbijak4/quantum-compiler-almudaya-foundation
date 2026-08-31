"""
Module 6 Stage 5 — Deterministic Provenance Logging.

Generates deterministic provenance records for Stage 5 extension experiments.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import hashlib
import json


@dataclass(frozen=True)
class Stage5Provenance:
    """
    Deterministic provenance record for Stage 5 expressibility experiments.
    """
    experiment_id: str
    compiler_version: str
    module: str
    stage: str
    base_vocabulary_hash: str
    candidate_gate_hash: str
    extended_vocabulary_hash: str
    target_operator_hash: str
    equivalence_policy: str
    numerical_tolerance: float
    search_parameters: Dict[str, Any]
    seed: Optional[int]
    evidence_classification: str
    deterministic_analysis_id: str = field(init=False)

    def __post_init__(self) -> None:
        raw_det = (
            f"{self.experiment_id}|{self.base_vocabulary_hash}|"
            f"{self.candidate_gate_hash}|{self.target_operator_hash}|"
            f"{self.evidence_classification}|{self.seed}"
        )
        det_id = hashlib.sha256(raw_det.encode("utf-8")).hexdigest()
        object.__setattr__(self, "deterministic_analysis_id", det_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "compiler_version": self.compiler_version,
            "module": self.module,
            "stage": self.stage,
            "base_vocabulary_hash": self.base_vocabulary_hash,
            "candidate_gate_hash": self.candidate_gate_hash,
            "extended_vocabulary_hash": self.extended_vocabulary_hash,
            "target_operator_hash": self.target_operator_hash,
            "equivalence_policy": self.equivalence_policy,
            "numerical_tolerance": self.numerical_tolerance,
            "search_parameters": dict(sorted(self.search_parameters.items())),
            "seed": self.seed,
            "evidence_classification": self.evidence_classification,
            "deterministic_analysis_id": self.deterministic_analysis_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stage5Provenance":
        return cls(
            experiment_id=data["experiment_id"],
            compiler_version=data.get("compiler_version", "1.0.0"),
            module=data.get("module", "Module 6"),
            stage=data.get("stage", "Stage 5"),
            base_vocabulary_hash=data["base_vocabulary_hash"],
            candidate_gate_hash=data["candidate_gate_hash"],
            extended_vocabulary_hash=data["extended_vocabulary_hash"],
            target_operator_hash=data["target_operator_hash"],
            equivalence_policy=data.get("equivalence_policy", "MULTI_LEVEL_STAGE4"),
            numerical_tolerance=data.get("numerical_tolerance", 1e-12),
            search_parameters=data.get("search_parameters", {}),
            seed=data.get("seed"),
            evidence_classification=data.get("evidence_classification", "EMPIRICAL_EXPERIMENT"),
        )
