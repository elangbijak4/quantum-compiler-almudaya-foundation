"""
Module 4 Foundation Package — Specifications & Data Models.
"""

from src.module4.foundation.domain import (
    FiniteDomainContract,
    FiniteDomainValidationResult,
)
from src.module4.foundation.encoding import (
    RegisterEncodingSpec,
    compute_register_encoding_spec,
    encode_configuration,
    verify_encoding_injectivity,
)
from src.module4.foundation.embedding import (
    FiniteHilbertEmbedding,
    RestrictedUnitaryContract,
)
from src.module4.foundation.gates import (
    LogicalPrimitiveGateType,
    LogicalPrimitiveGate,
)
from src.module4.foundation.policy import (
    NUMERICAL_VERIFICATION_TOLERANCE,
    VerificationLevel,
    VerificationPolicy,
)

__all__ = [
    "FiniteDomainContract",
    "FiniteDomainValidationResult",
    "RegisterEncodingSpec",
    "compute_register_encoding_spec",
    "encode_configuration",
    "verify_encoding_injectivity",
    "FiniteHilbertEmbedding",
    "RestrictedUnitaryContract",
    "LogicalPrimitiveGateType",
    "LogicalPrimitiveGate",
    "NUMERICAL_VERIFICATION_TOLERANCE",
    "VerificationLevel",
    "VerificationPolicy",
]
