"""
Module 6 Mapping Subpackage.

Provides semantic correspondence mapping, compiler mapper, identity representation, and quotient well-definedness analyzer.
"""

from src.module6.mapping.correspondence import BasisCorrespondenceRecord
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

__all__ = [
    "BasisCorrespondenceRecord",
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
]
