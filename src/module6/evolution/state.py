"""
Module 6 Stage 6 — Evolutionary Vocabulary State.

Defines immutable EvolutionaryVocabularyState tracking compiler vocabulary GE(k) across evolutionary lineage.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


@dataclass(frozen=True)
class EvolutionaryVocabularyState:
    """
    Immutable representation of the compiler's evolutionary gate vocabulary state GE(k).
    
    Invariants:
    1. GE(0) = G0 = {"X", "CNOT", "TOFFOLI"}
    2. Monotonicity: GE(k) subseteq GE(k+1)
    3. Reproducible lineage with cryptographic parent_vocabulary_hash and vocabulary_hash.
    """
    evolution_stage_id: str
    parent_stage_id: Optional[str]
    vocabulary: Tuple[str, ...]
    parent_vocabulary_hash: str
    vocabulary_hash: str
    promoted_gates: Tuple[str, ...]
    promotion_records: Tuple[Any, ...]
    provenance: Dict[str, Any] = field(default_factory=dict)
    compiler_version: str = "1.0.0"

    def __post_init__(self) -> None:
        if not self.vocabulary:
            raise ValueError("EvolutionaryVocabularyState vocabulary cannot be empty.")
        # Ensure vocabulary is sorted tuple
        sorted_vocab = tuple(sorted(set(self.vocabulary)))
        if self.vocabulary != sorted_vocab:
            object.__setattr__(self, "vocabulary", sorted_vocab)

        computed_hash = hashlib.sha256(json.dumps(self.vocabulary).encode("utf-8")).hexdigest()
        if self.vocabulary_hash != computed_hash:
            object.__setattr__(self, "vocabulary_hash", computed_hash)

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        prom_recs = [
            pr.to_dict() if hasattr(pr, "to_dict") else pr for pr in self.promotion_records
        ]
        return {
            "evolution_stage_id": self.evolution_stage_id,
            "parent_stage_id": self.parent_stage_id,
            "vocabulary": list(self.vocabulary),
            "parent_vocabulary_hash": self.parent_vocabulary_hash,
            "vocabulary_hash": self.vocabulary_hash,
            "promoted_gates": list(self.promoted_gates),
            "promotion_records": prom_recs,
            "provenance": dict(self.provenance),
            "compiler_version": self.compiler_version,
        }


def create_initial_evolutionary_state() -> EvolutionaryVocabularyState:
    """Creates initial evolutionary state GE(0) = G0 = {"X", "CNOT", "TOFFOLI"}."""
    g0 = ("CNOT", "TOFFOLI", "X")
    sorted_g0 = tuple(sorted(g0))
    g0_hash = hashlib.sha256(json.dumps(sorted_g0).encode("utf-8")).hexdigest()

    return EvolutionaryVocabularyState(
        evolution_stage_id="GE_0",
        parent_stage_id=None,
        vocabulary=sorted_g0,
        parent_vocabulary_hash="0" * 64,
        vocabulary_hash=g0_hash,
        promoted_gates=(),
        promotion_records=(),
        provenance={"creator": "Module 6 Stage 6 Initializer", "mode": "BASE_G0"},
        compiler_version="1.0.0",
    )
