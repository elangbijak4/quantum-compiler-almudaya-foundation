"""
Module 6 Stage 10 Test Suite — Initialization & Constitutional Verification.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.governance import (
    CertificationLevel,
    LifecycleStatus,
    GovernanceAuditor,
)
from src.module6.analysis.stage10 import analyze_stage10_governance


class TestStage10Initialization(unittest.TestCase):
    """Tests verifying Stage 10 initialization, scaffold, and constitutional invariants."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_scaffold_existence(self) -> None:
        """Verifies Stage 10 governance models and auditor exist."""
        report = analyze_stage10_governance(self.circuit, self.ctx)
        self.assertIsNotNone(report.audit_id)
        self.assertEqual(report.certificate.algorithm_id, self.circuit.circuit_id)

    def test_02_certification_level_enum(self) -> None:
        """Verifies CertificationLevel values."""
        self.assertEqual(CertificationLevel.FULLY_GOVERNED_CERTIFIED.value, "FULLY_GOVERNED_CERTIFIED")
        self.assertEqual(CertificationLevel.UNCERTIFIED.value, "UNCERTIFIED")

    def test_03_lifecycle_status_enum(self) -> None:
        """Verifies LifecycleStatus values."""
        self.assertEqual(LifecycleStatus.VERIFIED.value, "VERIFIED")
        self.assertEqual(LifecycleStatus.REJECTED.value, "REJECTED")

    def test_04_hardware_boundary_preserved(self) -> None:
        """Verifies hardware boundary is preserved (0% hardware execution)."""
        report = analyze_stage10_governance(self.circuit, self.ctx)
        self.assertGreater(len(report.findings), 0)
        self.assertEqual(report.findings[0].category.value, "SEMANTIC")


if __name__ == "__main__":
    unittest.main()
