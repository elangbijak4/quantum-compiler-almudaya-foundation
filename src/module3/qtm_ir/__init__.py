"""
Module 3 QTM-IR Package — Quantum Turing Machine Intermediate Representation.

Provides canonical data models, semantic validation engine, and deterministic JSON serialization.
"""

from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    QTM_IR_VERSION,
    CANONICAL_SEMANTIC_RELATION,
)
from src.module3.qtm_ir.validator import (
    validate_qtm_ir,
    ValidationResult,
    ValidationDiagnostic,
    DiagnosticCode,
    ValidationSeverity,
)
from src.module3.qtm_ir.serialization import (
    serialize_qtm_ir,
    deserialize_qtm_ir,
    serialize_qtm_ir_to_json,
    deserialize_qtm_ir_from_json,
)

__all__ = [
    "QTMIRModel",
    "QTMIRBasisState",
    "QTMIRStateVector",
    "QTMIRTransitionMapping",
    "QTMIRMatrixRepresentation",
    "QTMIRProvenance",
    "QTMIRComplexNumber",
    "QTM_IR_VERSION",
    "CANONICAL_SEMANTIC_RELATION",
    "validate_qtm_ir",
    "ValidationResult",
    "ValidationDiagnostic",
    "DiagnosticCode",
    "ValidationSeverity",
    "serialize_qtm_ir",
    "deserialize_qtm_ir",
    "serialize_qtm_ir_to_json",
    "deserialize_qtm_ir_from_json",
]
