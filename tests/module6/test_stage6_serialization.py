"""
Module 6 Stage 6 Test Suite — Canonical JSON Round-trip Serialization.
"""

import unittest

from src.module6.classical.semantic import create_sample_adder_model
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.serialization import serialize_session_baseline, deserialize_session_baseline
from src.module6.feasibility.analyzer import CompilationFeasibilityAnalyzer
from src.module6.feasibility.serialization import serialize_feasibility_report, deserialize_feasibility_report
from src.module6.integration.context import CompilerContext
from src.module6.integration.result import serialize_compilation_result, deserialize_compilation_result


class TestStage6Serialization(unittest.TestCase):
    """Tests for Canonical JSON Serialization deserialization round-trip."""

    def test_session_baseline_serialization_roundtrip(self) -> None:
        """Req 28: SessionBaseline serialization roundtrip."""
        ge0 = create_initial_evolutionary_state()
        sb = SessionBaseline(
            session_id="s123",
            selected_gates=("CNOT", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
            provenance={"test": True},
        )

        s_json = serialize_session_baseline(sb)
        des_sb = deserialize_session_baseline(s_json)

        self.assertEqual(des_sb.session_id, sb.session_id)
        self.assertEqual(des_sb.selected_gates, sb.selected_gates)
        self.assertEqual(des_sb.baseline_mode, sb.baseline_mode)

    def test_feasibility_report_serialization_roundtrip(self) -> None:
        """Req 28: CompilationFeasibilityReport serialization roundtrip."""
        ge0 = create_initial_evolutionary_state()
        sb = SessionBaseline(
            session_id="s123",
            selected_gates=ge0.vocabulary,
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=ge0.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
        )
        adder = create_sample_adder_model()
        rep = CompilationFeasibilityAnalyzer.analyze_feasibility(adder, ge0, sb)

        r_json = serialize_feasibility_report(rep)
        des_rep = deserialize_feasibility_report(r_json)

        self.assertEqual(des_rep.algorithm_id, rep.algorithm_id)
        self.assertEqual(des_rep.feasibility_status, rep.feasibility_status)

    def test_compilation_result_serialization_roundtrip(self) -> None:
        """Req 28: CompilationResult serialization roundtrip."""
        adder = create_sample_adder_model()
        ctx = CompilerContext()
        res = ctx.compile(adder)

        res_json = serialize_compilation_result(res)
        des_res = deserialize_compilation_result(res_json)

        self.assertEqual(des_res.source_algorithm_id, res.source_algorithm_id)
        self.assertEqual(des_res.compilation_status, res.compilation_status)
        self.assertEqual(des_res.circuit_id, res.circuit_id)


if __name__ == "__main__":
    unittest.main()
