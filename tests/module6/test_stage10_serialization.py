"""
Module 6 Stage 10 Test Suite — Canonical Serialization Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.governance import (
    serialize_audit_certificate,
    deserialize_audit_certificate,
    serialize_governance_finding,
    deserialize_governance_finding,
    serialize_governance_audit_report,
    deserialize_governance_audit_report,
)


class TestStage10Serialization(unittest.TestCase):
    """Tests verifying canonical JSON serialization and roundtrip equality deserialize(serialize(X)) == X."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_audit_certificate_roundtrip(self) -> None:
        """Verifies deserialize(serialize(AuditCertificate)) == AuditCertificate."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)

        cert = audit_report.certificate
        ser = serialize_audit_certificate(cert)
        des = deserialize_audit_certificate(ser)

        self.assertEqual(des.certificate_id, cert.certificate_id)
        self.assertEqual(des.certification_level, cert.certification_level)
        self.assertEqual(des.lifecycle_status, cert.lifecycle_status)
        self.assertEqual(des.provenance_hash, cert.provenance_hash)

        ser2 = serialize_audit_certificate(des)
        self.assertEqual(ser, ser2)

    def test_02_governance_audit_report_roundtrip(self) -> None:
        """Verifies deserialize(serialize(GovernanceAuditReport)) == GovernanceAuditReport."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)

        ser = serialize_governance_audit_report(audit_report)
        des = deserialize_governance_audit_report(ser)

        self.assertEqual(des.audit_id, audit_report.audit_id)
        self.assertEqual(des.report_hash, audit_report.report_hash)
        self.assertEqual(des.certificate.certification_level, audit_report.certificate.certification_level)

        ser2 = serialize_governance_audit_report(des)
        self.assertEqual(ser, ser2)


if __name__ == "__main__":
    unittest.main()
