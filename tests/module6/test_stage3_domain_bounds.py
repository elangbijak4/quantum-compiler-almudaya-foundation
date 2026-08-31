"""
Module 6 Stage 3 Unit Test Suite — Domain Bounds & Cardinality Analysis.

Verifies domain bounds, totality, determinism, reversibility, and cardinality bound descriptors.
"""

import unittest
from src.module6 import (
    AlgorithmFamilyGenerator,
    DomainBoundsAnalyzer,
    MappingTotalityStatus,
    CardinalityType,
)


class TestStage3DomainBounds(unittest.TestCase):
    def test_01_domain_bounds_all_families(self) -> None:
        """Positive test: DomainBoundsAnalyzer over multiple algorithm families."""
        fam1 = AlgorithmFamilyGenerator.generate_family("bit_flip_family", size=2)
        fam2 = AlgorithmFamilyGenerator.generate_family("controlled_transition_family", size=2)
        models = list(fam1.models) + list(fam2.models)

        desc, card, status = DomainBoundsAnalyzer.analyze_domain(models)

        self.assertEqual(status, MappingTotalityStatus.TOTAL_OVER_DEFINED_DOMAIN)
        self.assertEqual(card.cardinality_type, CardinalityType.COUNTABLE)
        self.assertTrue(card.is_formally_proven)
        self.assertEqual(card.exact_sample_size, 4)

    def test_02_negative_invalid_domain_model(self) -> None:
        """Negative test: DomainBoundsAnalyzer detects non-total/missing domain contract."""
        fam = AlgorithmFamilyGenerator.generate_family("two_state_cycle_family", size=1)
        m = fam.models[0]

        # Mutate to create corrupted model missing domain_contract
        corrupted_m = type(m)(
            algorithm_id=m.algorithm_id,
            source_program_hash=m.source_program_hash,
            domain_contract=None,  # missing domain contract
            encoding_spec=m.encoding_spec,
            state_map=m.state_map,
            symbol_map=m.symbol_map,
            transition_table=m.transition_table,
        )

        desc, card, status = DomainBoundsAnalyzer.analyze_domain([corrupted_m])
        self.assertEqual(status, MappingTotalityStatus.PARTIAL)
        self.assertFalse(desc.is_totality_verified)


if __name__ == "__main__":
    unittest.main()
