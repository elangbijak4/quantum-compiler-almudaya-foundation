"""
Verification Module: Dual Execution, Semantic Equivalence Verification & Certificate C1.
"""

from .dual import (
    DualExecutionResult,
    execute_dual_pipeline,
)

from .verifier import (
    SemanticVerificationResult,
    extract_obs_aml,
    extract_obs_utm,
    verify_semantic_equivalence,
)

from .certificate import (
    CertificateC1,
    generate_certificate_c1,
    serialize_certificate_c1,
    hash_certificate_c1,
    validate_certificate_c1,
    save_certificate_c1,
)

__all__ = [
    "DualExecutionResult",
    "execute_dual_pipeline",
    "SemanticVerificationResult",
    "extract_obs_aml",
    "extract_obs_utm",
    "verify_semantic_equivalence",
    "CertificateC1",
    "generate_certificate_c1",
    "serialize_certificate_c1",
    "hash_certificate_c1",
    "validate_certificate_c1",
    "save_certificate_c1",
]
