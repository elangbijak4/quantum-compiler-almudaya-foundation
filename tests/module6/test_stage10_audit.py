"""
Module 6 Stage 10 Test Suite — Governance Audit Engine Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.governance import (
    CertificationLevel,
    LifecycleStatus,
    GovernanceAuditor,
)


class TestStage10Audit(unittest.TestCase):
    """Tests verifying GovernanceAuditor audit execution across Stages 1–9."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_successful_compilation_audit(self) -> None:
        """Verifies full audit pipeline produces FULLY_GOVERNED_CERTIFIED for valid verified compilation."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)

        self.assertEqual(audit_report.certificate.certification_level, CertificationLevel.FULLY_GOVERNED_CERTIFIED)
        self.assertEqual(audit_report.certificate.lifecycle_status, LifecycleStatus.CERTIFIED)
        self.assertTrue(audit_report.certificate.stage4_verified)
        self.assertTrue(audit_report.certificate.stage7_feasible)
        self.assertTrue(audit_report.certificate.stage9_quality_passed)
        self.assertIsNotNone(audit_report.report_hash)

    def test_02_audit_findings_generation(self) -> None:
        """Verifies structured GovernanceFindings are recorded for all audit categories."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)

        self.assertGreater(len(audit_report.findings), 0)
        categories = [f.category for f in audit_report.findings]
        self.assertIn("SEMANTIC", categories)
        self.assertIn("VOCABULARY", categories)


if __name__ == "__main__":
    unittest.main()
