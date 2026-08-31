"""
Module 6 Stage 5/6 — Extended Gate Vocabulary & Evolving Compiler Analysis Subpackage.
"""

from src.module6.evolution.candidate import CandidateGate, compute_canonical_matrix_hash
from src.module6.evolution.target import (
    TargetOperator,
    get_reference_target_hadamard,
    get_reference_target_phase,
    get_reference_target_t,
)
from src.module6.evolution.registry import (
    CandidateRegistry,
    compute_base_vocabulary_hash,
    BASE_PRIMITIVE_NAMES,
)
from src.module6.evolution.metrics import ExpressiveGainMetrics
from src.module6.evolution.provenance import Stage5Provenance
from src.module6.evolution.extension import (
    ExtensionClassification,
    ExtensionReport,
    ExtendedVocabularyEvaluator,
)
from src.module6.evolution.analyzer import EvolvingCompilerAnalyzer
from src.module6.evolution.serialization import (
    serialize_stage5_object,
    deserialize_candidate_gate,
    deserialize_target_operator,
    deserialize_extension_report,
)

from src.module6.evolution.state import EvolutionaryVocabularyState, create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager

__all__ = [
    "CandidateGate",
    "compute_canonical_matrix_hash",
    "TargetOperator",
    "get_reference_target_hadamard",
    "get_reference_target_phase",
    "get_reference_target_t",
    "CandidateRegistry",
    "compute_base_vocabulary_hash",
    "BASE_PRIMITIVE_NAMES",
    "ExpressiveGainMetrics",
    "Stage5Provenance",
    "ExtensionClassification",
    "ExtensionReport",
    "ExtendedVocabularyEvaluator",
    "EvolvingCompilerAnalyzer",
    "serialize_stage5_object",
    "deserialize_candidate_gate",
    "deserialize_target_operator",
    "deserialize_extension_report",
    "EvolutionaryVocabularyState",
    "create_initial_evolutionary_state",
    "PromotionRecord",
    "PromotionAuthorizationStatus",
    "EvolutionaryLineageManager",
]
