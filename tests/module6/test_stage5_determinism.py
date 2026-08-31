"""
Module 6 Stage 5 Unit Test Suite — Deterministic Execution.

Verifies deterministic execution and byte-identical JSON report outputs across repeated runs.
"""

import unittest
from src.module6.analysis.stage5 import analyze_evolving_compiler_stage5
from src.module6.evolution import serialize_stage5_object


class TestStage5Determinism(unittest.TestCase):
    def test_01_repeated_analysis_determinism(self) -> None:
        """Positive test: Repeated Stage 5 analysis yields identical deterministic_analysis_id and JSON."""
        rep1 = analyze_evolving_compiler_stage5(seed=123)
        rep2 = analyze_evolving_compiler_stage5(seed=123)

        self.assertEqual(rep1.deterministic_analysis_id, rep2.deterministic_analysis_id)
        json1 = serialize_stage5_object(rep1)
        json2 = serialize_stage5_object(rep2)
        self.assertEqual(json1, json2)


if __name__ == "__main__":
    unittest.main()
