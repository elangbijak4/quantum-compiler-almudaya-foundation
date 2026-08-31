"""
Module 6 Stage 6 Test Suite — Determinism.
"""

import unittest

from src.module6.classical.semantic import create_sample_adder_model
from src.module6.integration.context import CompilerContext
from src.module6.integration.result import serialize_compilation_result
from src.module6.analysis.stage6 import analyze_stage6_evolution_and_feasibility


class TestStage6Determinism(unittest.TestCase):
    """Tests for Stage 6 Determinism."""

    def test_compilation_result_determinism(self) -> None:
        """Req 27: Repeated compilation produces byte-identical JSON serialized output."""
        adder = create_sample_adder_model()
        ctx = CompilerContext()

        res1 = ctx.compile(adder)
        res2 = ctx.compile(adder)

        json1 = serialize_compilation_result(res1)
        json2 = serialize_compilation_result(res2)

        self.assertEqual(json1, json2)

    def test_stage6_master_analysis_determinism(self) -> None:
        """Req 27: Master analysis execution is deterministic."""
        rep1 = analyze_stage6_evolution_and_feasibility()
        rep2 = analyze_stage6_evolution_and_feasibility()

        self.assertEqual(rep1.to_dict(), rep2.to_dict())


if __name__ == "__main__":
    unittest.main()
