"""
Module 6 — Classical-to-Quantum Expressibility & Equivalence Analysis.

Top-level package exports for Stages 1, 2, 3, 4, 5, and 6.
"""

__version__ = "1.0.0"
__status__ = "STAGE_6_COMPILATION_FEASIBILITY_COMPLETE"

from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.classical.transition import build_classical_semantic_model
from src.module6.mapping.mapper import CompilerMapper
from src.module6.mapping.identity import (
    ClassicalAlgorithmIdentity,
    create_classical_algorithm_identity,
)
from src.module6.mapping.model import (
    DomainDescriptor,
    CodomainDescriptor,
    CompilerMappingRecord,
    SemanticQuotientRecord,
    MappingComplexityRecord,
    MappingTotalityStatus,
    QuotientWellDefinednessStatus,
    BoundClassification,
)
from src.module6.mapping.quotient import QuotientWellDefinednessAnalyzer
from src.module6.mapping.preservation import ClassicalEquivalenceEvaluator, MappingPreservationEvaluator
from src.module6.mapping.collision import CollisionAnalyzer, CollisionType, CollisionRecord
from src.module6.mapping.analyzer import MappingAnalyzer

from src.module6.equivalence.verifier import Stage1SemanticVerifier
from src.module6.equivalence.report import (
    SemanticEquivalenceReport,
    EquivalenceReport,
    EquivalenceStatus,
    FailureCode,
    serialize_report,
    deserialize_report,
)
from src.module6.equivalence.levels import EquivalenceLevel
from src.module6.equivalence.syntactic import SyntacticEquivalenceEvaluator
from src.module6.equivalence.structural import StructuralEquivalenceEvaluator
from src.module6.equivalence.basis import BasisEquivalenceEvaluator, Level3BasisVerifier
from src.module6.equivalence.state_vector import StateVectorEquivalenceEvaluator
from src.module6.equivalence.phase import PhaseOverlapEvaluator
from src.module6.equivalence.operator import Level5OperatorVerifier
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator

from src.module6.bounds.domain import DomainBoundsAnalyzer
from src.module6.bounds.codomain import CodomainBoundsAnalyzer
from src.module6.bounds.image import ImageBoundsAnalyzer, ImageBound
from src.module6.bounds.cardinality import CardinalityType, CardinalityBound

from src.module6.image.characterization import EmpiricalImageCharacterizer, EmpiricalImageSummary
from src.module6.image.signature import compute_circuit_unitary, compute_image_signature

from src.module6.targets.builder import TargetCatalogBuilder

from src.module6.vocabulary.analyzer import (
    PrimitiveVocabularyAnalyzer,
    PrimitiveVocabularyReachabilityStatus,
)

from src.module6.expressibility.config import ExpressibilityExperimentConfig
from src.module6.expressibility.report import (
    TargetReachabilityStatus,
    InjectivityStatus,
    SurjectivityStatus,
    UniversalExpressibilityStatus,
    Stage2FailureCode,
    serialize_expressibility_report,
    deserialize_expressibility_report,
)

from src.module6.invariants.permutation import PermutationInvariantAnalyzer
from src.module6.invariants.amplitude import RealAmplitudeInvariantAnalyzer
from src.module6.invariants.composition import (
    SuperpositionCapabilityAnalyzer,
    CompositionClosureAnalyzer,
    InverseClosureAnalyzer,
    IdentityElementAnalyzer,
)
from src.module6.invariants.analyzer import StructuralInvariantAnalyzer, StructuralInvariantResult

from src.module6.families.generators import AlgorithmFamilyGenerator

from src.module6.analysis.stage1 import analyze_classical_algorithm_stage1
from src.module6.analysis.stage2 import analyze_compiler_image_stage2
from src.module6.analysis.stage3 import analyze_compiler_mapping_stage3
from src.module6.analysis.stage4 import analyze_compiler_mapping_stage4
from src.module6.analysis.stage5 import analyze_evolving_compiler_stage5, Stage5AnalysisReport
from src.module6.analysis.stage6 import analyze_stage6_evolution_and_feasibility, Stage6AnalysisReport
from src.module6.analysis.report import (
    Stage3AnalysisReport,
    Stage3FailureCode,
    serialize_stage3_report,
    deserialize_stage3_report,
)

from src.module6.evolution import (
    CandidateGate,
    TargetOperator,
    CandidateRegistry,
    EvolvingCompilerAnalyzer,
    ExtensionClassification,
    ExtensionReport,
    ExpressiveGainMetrics,
    Stage5Provenance,
    EvolutionaryVocabularyState,
    create_initial_evolutionary_state,
    PromotionRecord,
    PromotionAuthorizationStatus,
    EvolutionaryLineageManager,
    get_reference_target_hadamard,
    get_reference_target_phase,
    get_reference_target_t,
)
from src.module6.session import SessionBaseline, BaselineMode, EffectiveVocabularyResolver, SessionLifecycle
from src.module6.feasibility import FeasibilityStatus, DiagnosisLevel, CompilationFeasibilityReport, CompilationFeasibilityAnalyzer, MinimalAugmentationAnalyzer
from src.module6.integration import CompilationStatus, CompilationResult, CompilerContext

__all__ = [
    "__version__",
    "__status__",
    "ClassicalSemanticModel",
    "build_classical_semantic_model",
    "CompilerMapper",
    "ClassicalAlgorithmIdentity",
    "create_classical_algorithm_identity",
    "DomainDescriptor",
    "CodomainDescriptor",
    "CompilerMappingRecord",
    "SemanticQuotientRecord",
    "MappingComplexityRecord",
    "MappingTotalityStatus",
    "QuotientWellDefinednessStatus",
    "BoundClassification",
    "QuotientWellDefinednessAnalyzer",
    "ClassicalEquivalenceEvaluator",
    "MappingPreservationEvaluator",
    "CollisionAnalyzer",
    "CollisionType",
    "CollisionRecord",
    "MappingAnalyzer",
    "Stage1SemanticVerifier",
    "SemanticEquivalenceReport",
    "EquivalenceReport",
    "EquivalenceStatus",
    "FailureCode",
    "serialize_report",
    "deserialize_report",
    "EquivalenceLevel",
    "SyntacticEquivalenceEvaluator",
    "StructuralEquivalenceEvaluator",
    "BasisEquivalenceEvaluator",
    "Level3BasisVerifier",
    "StateVectorEquivalenceEvaluator",
    "PhaseOverlapEvaluator",
    "Level5OperatorVerifier",
    "SemanticEquivalenceEvaluator",
    "DomainBoundsAnalyzer",
    "CodomainBoundsAnalyzer",
    "ImageBoundsAnalyzer",
    "ImageBound",
    "CardinalityType",
    "CardinalityBound",
    "EmpiricalImageCharacterizer",
    "EmpiricalImageSummary",
    "compute_circuit_unitary",
    "compute_image_signature",
    "TargetCatalogBuilder",
    "PrimitiveVocabularyAnalyzer",
    "PrimitiveVocabularyReachabilityStatus",
    "ExpressibilityExperimentConfig",
    "TargetReachabilityStatus",
    "InjectivityStatus",
    "SurjectivityStatus",
    "UniversalExpressibilityStatus",
    "Stage2FailureCode",
    "serialize_expressibility_report",
    "deserialize_expressibility_report",
    "PermutationInvariantAnalyzer",
    "RealAmplitudeInvariantAnalyzer",
    "SuperpositionCapabilityAnalyzer",
    "CompositionClosureAnalyzer",
    "InverseClosureAnalyzer",
    "IdentityElementAnalyzer",
    "StructuralInvariantAnalyzer",
    "StructuralInvariantResult",
    "AlgorithmFamilyGenerator",
    "analyze_classical_algorithm_stage1",
    "analyze_compiler_image_stage2",
    "analyze_compiler_mapping_stage3",
    "analyze_compiler_mapping_stage4",
    "analyze_evolving_compiler_stage5",
    "Stage5AnalysisReport",
    "analyze_stage6_evolution_and_feasibility",
    "Stage6AnalysisReport",
    "Stage3AnalysisReport",
    "Stage3FailureCode",
    "serialize_stage3_report",
    "deserialize_stage3_report",
    "CandidateGate",
    "TargetOperator",
    "CandidateRegistry",
    "EvolvingCompilerAnalyzer",
    "ExtensionClassification",
    "ExtensionReport",
    "ExpressiveGainMetrics",
    "Stage5Provenance",
    "EvolutionaryVocabularyState",
    "create_initial_evolutionary_state",
    "PromotionRecord",
    "PromotionAuthorizationStatus",
    "EvolutionaryLineageManager",
    "get_reference_target_hadamard",
    "get_reference_target_phase",
    "get_reference_target_t",
    "SessionBaseline",
    "BaselineMode",
    "EffectiveVocabularyResolver",
    "SessionLifecycle",
    "FeasibilityStatus",
    "DiagnosisLevel",
    "CompilationFeasibilityReport",
    "CompilationFeasibilityAnalyzer",
    "MinimalAugmentationAnalyzer",
    "CompilationResult",
    "CompilerContext",
    "ConfigurationStatus",
    "ConfigurationPrecedence",
    "ResolutionConflict",
    "EffectiveCompilationContext",
    "ResolutionResult",
    "ResolutionValidator",
    "ResolutionPolicy",
    "ConflictManager",
    "ResolutionProvenanceGenerator",
    "serialize_compilation_context",
    "deserialize_compilation_context",
    "Stage7CompilerResolver",
    "analyze_stage7_resolution_and_control",
    "Stage7AnalysisReport",
]

