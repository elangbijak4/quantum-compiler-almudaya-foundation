"""
Module 6 Stage 10 — Evolutionary Governance, Compilation Auditing & Lifecycle Certification Models.

Defines CertificationLevel, LifecycleStatus, FindingCategory, FindingSeverity,
GovernanceFinding, AuditCertificate, and GovernanceAuditReport.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib


class CertificationLevel(str, Enum):
    """Governed audit certification level for compilation artifacts."""
    UNCERTIFIED = "UNCERTIFIED"
    SEMANTICS_VERIFIED = "SEMANTICS_VERIFIED"
    FEASIBILITY_CERTIFIED = "FEASIBILITY_CERTIFIED"
    OPTIMIZATION_CERTIFIED = "OPTIMIZATION_CERTIFIED"
    FULLY_GOVERNED_CERTIFIED = "FULLY_GOVERNED_CERTIFIED"
    AUDIT_FAILED = "AUDIT_FAILED"

    def __str__(self) -> str:
        return self.value


class LifecycleStatus(str, Enum):
    """Lifecycle status of compiled quantum artifacts."""
    CANDIDATE = "CANDIDATE"
    ANALYZED = "ANALYZED"
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"
    GOVERNED = "GOVERNED"
    CERTIFIED = "CERTIFIED"
    DEPRECATED = "DEPRECATED"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"

    def __str__(self) -> str:
        return self.value


class FindingCategory(str, Enum):
    """Structured categories for governance audit findings."""
    SEMANTIC = "SEMANTIC"
    VOCABULARY = "VOCABULARY"
    BASELINE = "BASELINE"
    RESOURCE = "RESOURCE"
    PROVENANCE = "PROVENANCE"
    CONFIGURATION = "CONFIGURATION"
    LIFECYCLE = "LIFECYCLE"
    GOVERNANCE = "GOVERNANCE"
    CERTIFICATION = "CERTIFICATION"

    def __str__(self) -> str:
        return self.value


class FindingSeverity(str, Enum):
    """Severity levels for audit findings."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class GovernanceFinding:
    """
    Structured governance audit finding representing evidence-backed compliance or failure.
    """
    finding_id: str
    category: FindingCategory
    severity: FindingSeverity
    status: str
    evidence: str
    policy_or_invariant: str
    consequence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "status": self.status,
            "evidence": self.evidence,
            "policy_or_invariant": self.policy_or_invariant,
            "consequence": self.consequence,
        }


@dataclass(frozen=True)
class AuditCertificate:
    """
    Immutable audit certificate produced by Stage 10 governance evaluator.
    """
    certificate_id: str
    algorithm_id: str
    certification_level: CertificationLevel
    lifecycle_status: LifecycleStatus
    stage4_verified: bool
    stage7_feasible: bool
    stage8_optimized: bool
    stage9_quality_passed: bool
    provenance_hash: str
    prerequisites_satisfied: Tuple[str, ...]
    prerequisites_failed: Tuple[str, ...]
    identity_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "algorithm_id": self.algorithm_id,
            "certification_level": self.certification_level.value,
            "lifecycle_status": self.lifecycle_status.value,
            "stage4_verified": self.stage4_verified,
            "stage7_feasible": self.stage7_feasible,
            "stage8_optimized": self.stage8_optimized,
            "stage9_quality_passed": self.stage9_quality_passed,
            "provenance_hash": self.provenance_hash,
            "prerequisites_satisfied": list(self.prerequisites_satisfied),
            "prerequisites_failed": list(self.prerequisites_failed),
            "identity_hash": self.identity_hash,
        }


@dataclass(frozen=True)
class GovernanceAuditReport:
    """
    Master Stage 10 Governance Audit & Lifecycle Report.
    """
    audit_id: str
    algorithm_id: str
    certificate: AuditCertificate
    findings: Tuple[GovernanceFinding, ...]
    provenance: Dict[str, Any] = field(default_factory=dict)
    report_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "algorithm_id": self.algorithm_id,
            "certificate": self.certificate.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "provenance": dict(self.provenance),
            "report_hash": self.report_hash,
        }
