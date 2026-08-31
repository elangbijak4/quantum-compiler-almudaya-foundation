"""
Module 6 Stage 10 Test Suite — Audit Certificate & Certification Level Tests.
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
)


class TestStage10Certification(unittest.TestCase):
    """Tests verifying AuditCertificate level assignment based on evidence."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_prerequisites_tracking(self) -> None:
        """Verifies AuditCertificate accurately records satisfied and failed prerequisites."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)

        cert = audit_report.certificate
        self.assertIn("STAGE_4_SEMANTIC_VERIFICATION_PASSED", cert.prerequisites_satisfied)
        self.assertIn("STAGE_7_FEASIBILITY_PASSED", cert.prerequisites_satisfied)
        self.assertIn("STAGE_9_QUALITY_PASSED", cert.prerequisites_satisfied)
        self.assertEqual(len(cert.prerequisites_failed), 0)


if __name__ == "__main__":
    unittest.main()
