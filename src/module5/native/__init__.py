"""
Module 5 Stage 4 Native Gate Translation Package.
"""

from src.module5.native.model import (
    NativeGateDefinition,
    NativeOperation,
    NativeResolutionStatus,
    NativeGateResolutionResult,
    NativeCircuitIR,
    NativeTranslationResult,
    SCHEMA_VERSION as NATIVE_SCHEMA_VERSION,
)
from src.module5.native.vocabulary import NativeGateVocabulary
from src.module5.native.registry import DecompositionEntry, GateDecompositionRegistry
from src.module5.native.adapter import BackendAdapter, ReferenceBackendAdapter
from src.module5.native.validator import NativeCircuitValidationResult, validate_native_circuit_ir
from src.module5.native.verifier import SemanticVerificationReport, NativeCircuitVerifier
from src.module5.native.translator import NativeTranslator
from src.module5.native.serialization import serialize_native_circuit_ir, deserialize_native_circuit_ir

__all__ = [
    "NativeGateDefinition",
    "NativeOperation",
    "NativeResolutionStatus",
    "NativeGateResolutionResult",
    "NativeCircuitIR",
    "NativeTranslationResult",
    "NATIVE_SCHEMA_VERSION",
    "NativeGateVocabulary",
    "DecompositionEntry",
    "GateDecompositionRegistry",
    "BackendAdapter",
    "ReferenceBackendAdapter",
    "NativeCircuitValidationResult",
    "validate_native_circuit_ir",
    "SemanticVerificationReport",
    "NativeCircuitVerifier",
    "NativeTranslator",
    "serialize_native_circuit_ir",
    "deserialize_native_circuit_ir",
]
