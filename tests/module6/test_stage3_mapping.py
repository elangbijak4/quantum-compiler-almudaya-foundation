"""
Module 6 Stage 3 Unit Test Suite — Mapping, Identity & Domain/Codomain Descriptors.

Verifies creation and invariants of ClassicalAlgorithmIdentity, DomainDescriptor, CodomainDescriptor,
and CompilerMappingRecord.
"""

import unittest
from src.module6 import (
    AlgorithmFamilyGenerator,
    CompilerMapper,
    create_classical_algorithm_identity,
    DomainBoundsAnalyzer,
    CodomainBoundsAnalyzer,
    MappingTotalityStatus,
    CardinalityType,
)


class TestStage3Mapping(unittest.TestCase):
    def setUp(self) -> None:
        self.family = AlgorithmFamilyGenerator.generate_family("identity_family", size=2)
        self.models = list(self.family.models)
        self.programs = list(self.family.programs)
        self.circuits = [CompilerMapper.map_classical_model(m, p) for m, p in zip(self.models, self.programs)]

    def test_01_classical_algorithm_identity_creation(self) -> None:
        """Positive test: Creation and immutability of ClassicalAlgorithmIdentity."""
        ident = create_classical_algorithm_identity(self.models[0], self.programs[0])
        self.assertEqual(ident.algorithm_id, self.models[0].algorithm_id)
        self.assertTrue(len(ident.program_hash) > 0)
        self.assertTrue(len(ident.domain_id) > 0)
        self.assertTrue(ident.is_syntactically_identical(ident))

    def test_02_domain_descriptor_and_totality(self) -> None:
        """Positive test: DomainBoundsAnalyzer generates valid DomainDescriptor and TOTALLY_DEFINED status."""
        desc, card, status = DomainBoundsAnalyzer.analyze_domain(self.models)
        self.assertEqual(desc.domain_name, "A_C")
        self.assertEqual(status, MappingTotalityStatus.TOTAL_OVER_DEFINED_DOMAIN)
        self.assertEqual(card.cardinality_type, CardinalityType.COUNTABLE)
        self.assertTrue(desc.is_totality_verified)
        self.assertTrue(desc.is_determinism_verified)

    def test_03_codomain_descriptor_and_complexity(self) -> None:
        """Positive test: CodomainBoundsAnalyzer generates valid CodomainDescriptor and complexity records."""
        desc, card, complexity_recs = CodomainBoundsAnalyzer.analyze_codomain(self.models, self.circuits)
        self.assertEqual(desc.codomain_name, "C_Q^logical")
        self.assertEqual(card.cardinality_type, CardinalityType.COUNTABLE)
        self.assertEqual(len(complexity_recs), 2)
        self.assertGreater(complexity_recs[0].logical_qubit_count, 0)
        self.assertGreaterEqual(complexity_recs[0].logical_gate_count, 0)


if __name__ == "__main__":
    unittest.main()
