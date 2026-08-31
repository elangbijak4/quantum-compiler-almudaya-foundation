"""
Module 6 Stage 10 — Governance Serialization.

Canonical JSON serialization and deserialization for AuditCertificate, GovernanceFinding,
and GovernanceAuditReport. Enforces deserialize(serialize(X)) == X.
"""

import json
from typing import Dict, Any
from src.module6.governance.model import (
    CertificationLevel,
    LifecycleStatus,
    FindingCategory,
    FindingSeverity,
    GovernanceFinding,
    AuditCertificate,
    GovernanceAuditReport,
)


def serialize_audit_certificate(cert: AuditCertificate) -> str:
    """Serializes AuditCertificate into canonical JSON string."""
    return json.dumps(cert.to_dict(), indent=2, sort_keys=True)


def deserialize_audit_certificate(json_str: str) -> AuditCertificate:
    """Deserializes canonical JSON string into AuditCertificate."""
    data = json.loads(json_str)
    return AuditCertificate(
        certificate_id=data["certificate_id"],
        algorithm_id=data["algorithm_id"],
        certification_level=CertificationLevel(data["certification_level"]),
        lifecycle_status=LifecycleStatus(data["lifecycle_status"]),
        stage4_verified=data["stage4_verified"],
        stage7_feasible=data["stage7_feasible"],
        stage8_optimized=data["stage8_optimized"],
        stage9_quality_passed=data["stage9_quality_passed"],
        provenance_hash=data["provenance_hash"],
        prerequisites_satisfied=tuple(data["prerequisites_satisfied"]),
        prerequisites_failed=tuple(data["prerequisites_failed"]),
        identity_hash=data.get("identity_hash", ""),
    )


def serialize_governance_finding(finding: GovernanceFinding) -> str:
    """Serializes GovernanceFinding into canonical JSON string."""
    return json.dumps(finding.to_dict(), indent=2, sort_keys=True)


def deserialize_governance_finding(json_str: str) -> GovernanceFinding:
    """Deserializes canonical JSON string into GovernanceFinding."""
    data = json.loads(json_str)
    return GovernanceFinding(
        finding_id=data["finding_id"],
        category=FindingCategory(data["category"]),
        severity=FindingSeverity(data["severity"]),
        status=data["status"],
        evidence=data["evidence"],
        policy_or_invariant=data["policy_or_invariant"],
        consequence=data["consequence"],
    )


def serialize_governance_audit_report(report: GovernanceAuditReport) -> str:
    """Serializes GovernanceAuditReport into canonical JSON string."""
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def deserialize_governance_audit_report(json_str: str) -> GovernanceAuditReport:
    """Deserializes canonical JSON string into GovernanceAuditReport."""
    data = json.loads(json_str)
    cert = deserialize_audit_certificate(json.dumps(data["certificate"]))
    findings = [
        deserialize_governance_finding(json.dumps(f_data)) for f_data in data["findings"]
    ]

    return GovernanceAuditReport(
        audit_id=data["audit_id"],
        algorithm_id=data["algorithm_id"],
        certificate=cert,
        findings=tuple(findings),
        provenance=dict(data["provenance"]),
        report_hash=data["report_hash"],
    )
