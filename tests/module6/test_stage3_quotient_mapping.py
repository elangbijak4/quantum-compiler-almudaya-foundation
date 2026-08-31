"""
Module 6 Stage 3 Unit Test Suite — Semantic Quotient Mapping F_bar Analysis.

Verifies quotient mapping F_bar: A_C/\equiv_C -> C_Q/\equiv_Q well-definedness testing.
"""

import unittest
from src.module6 import (
    AlgorithmFamilyGenerator,
    CompilerMapper,
    QuotientWellDefinednessAnalyzer,
    QuotientWellDefinednessStatus,
)


class TestStage3QuotientMapping(unittest.TestCase):
    def test_01_quotient_well_definedness_analysis(self) -> None:
        """Positive test: QuotientWellDefinednessAnalyzer evaluates well-definedness over algorithm sample."""
        fam1 = AlgorithmFamilyGenerator.generate_family("identity_family", size=2)
        fam2 = AlgorithmFamilyGenerator.generate_family("bit_flip_family", size=2)

        models = list(fam1.models) + list(fam2.models)
        programs = list(fam1.programs) + list(fam2.programs)
        circuits = [CompilerMapper.map_classical_model(m, p) for m, p in zip(models, programs)]

        status, records = QuotientWellDefinednessAnalyzer.analyze_quotient(models, circuits)
        self.assertIn(
            status,
            (
                QuotientWellDefinednessStatus.WELL_DEFINED_OBSERVED,
                QuotientWellDefinednessStatus.NOT_ESTABLISHED,
            ),
        )


if __name__ == "__main__":
    unittest.main()
