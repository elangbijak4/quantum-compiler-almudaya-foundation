"""
Module 6 Stage 1 Unit Test Suite — Semantic Mapping & Model Extraction.

Tests classical model extraction, compiler mapping observation F: A_C -> C_Q^logical,
determinism, input immutability, provenance preservation, and negative input validation.
"""

import unittest
import json
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module4 import FiniteDomainContract
from src.module6 import (
    build_classical_semantic_model,
    CompilerMapper,
    analyze_classical_algorithm_stage1,
    EquivalenceStatus,
    serialize_report,
    deserialize_report,
)


class TestStage1SemanticMapping(unittest.TestCase):
    def setUp(self) -> None:
        self.program = UTMProgram(
            states={"q0", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q0",
            halt_state="q_halt",
            transitions={
                ("q0", "0"): TransitionAction(next_state="q1", write_symbol="1", direction=Direction.RIGHT),
                ("q1", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT),
            },
        )

        self.c0 = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=0, history=(), step_count=0, halted=True)
        self.c1 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1"}, head_pos=1, history=(), step_count=0, halted=True)
        self.c2 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1", 2: "1"}, head_pos=2, history=(), step_count=0, halted=True)

        self.domain_contract = FiniteDomainContract(
            domain=[self.c0, self.c1, self.c2],
            execution_horizon=2,
            initial_configuration=self.c0,
        )

        self.state_map = {"q0": 0, "q1": 1, "q_halt": 2}
        self.symbol_map = {"_": 0, "0": 1, "1": 2}

    def test_01_classical_model_construction_pass(self) -> None:
        """Positive test: ClassicalSemanticModel construction succeeds with valid finite domain."""
        model = build_classical_semantic_model(
            program=self.program,
            domain_contract=self.domain_contract,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            algorithm_id="alg_test_01",
        )

        self.assertEqual(model.algorithm_id, "alg_test_01")
        self.assertEqual(len(model.transition_table), 3)
        self.assertTrue(len(model.compute_deterministic_id()) > 0)

    def test_02_compiler_mapping_observation_pass(self) -> None:
        """Positive test: CompilerMapper produces logical QuantumCircuitIR from ClassicalSemanticModel."""
        model = build_classical_semantic_model(
            program=self.program,
            domain_contract=self.domain_contract,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        circuit = CompilerMapper.map_classical_model(model, self.program)
        self.assertIsNotNone(circuit)
        self.assertEqual(circuit.circuit_id, "logical_default_alg")

    def test_03_end_to_end_stage1_analysis_pass(self) -> None:
        """Positive test: End-to-end Stage 1 analysis orchestrator PASS."""
        report = analyze_classical_algorithm_stage1(
            program=self.program,
            domain_contract=self.domain_contract,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            algorithm_id="alg_e2e_pass",
        )

        self.assertEqual(report.status, EquivalenceStatus.VERIFIED)
        self.assertEqual(report.level_3_status, EquivalenceStatus.VERIFIED)
        self.assertEqual(report.level_5_status, EquivalenceStatus.VERIFIED)
        self.assertTrue(report.ancilla_cleanliness_pass)
        self.assertTrue(report.global_phase_pass)
        self.assertTrue(report.reverse_equivalence_pass)

    def test_04_determinism_and_repeated_analysis(self) -> None:
        """Positive test: Repeated analysis produces identical report and deterministic_analysis_id."""
        rep1 = analyze_classical_algorithm_stage1(
            self.program, self.domain_contract, self.state_map, self.symbol_map, "alg_det"
        )
        rep2 = analyze_classical_algorithm_stage1(
            self.program, self.domain_contract, self.state_map, self.symbol_map, "alg_det"
        )

        self.assertEqual(rep1.deterministic_analysis_id, rep2.deterministic_analysis_id)
        self.assertEqual(rep1.status, rep2.status)
        self.assertEqual(rep1.operator_residual, rep2.operator_residual)

    def test_05_report_serialization_roundtrip(self) -> None:
        """Positive test: Report JSON serialization and deserialization roundtrip invariant."""
        report = analyze_classical_algorithm_stage1(
            self.program, self.domain_contract, self.state_map, self.symbol_map, "alg_ser"
        )

        json_str = serialize_report(report)
        reconstructed = deserialize_report(json_str)

        self.assertEqual(reconstructed.classical_algorithm_id, report.classical_algorithm_id)
        self.assertEqual(reconstructed.status, report.status)
        self.assertEqual(reconstructed.deterministic_analysis_id, report.deterministic_analysis_id)
        self.assertEqual(len(reconstructed.basis_results), len(report.basis_results))

    def test_06_negative_empty_domain_rejection(self) -> None:
        """Negative test: Rejects empty domain contract."""
        empty_contract = FiniteDomainContract(domain=[], execution_horizon=0)
        with self.assertRaises(Exception):
            build_classical_semantic_model(
                self.program, empty_contract, self.state_map, self.symbol_map
            )

    def test_07_negative_ambiguous_encoding_rejection(self) -> None:
        """Negative test: Rejects ambiguous/colliding state mapping where two configs get same bitstring."""
        c_a = RUTMConfiguration(current_state="q0", tape={0: "1"}, head_pos=0, history=(), step_count=0, halted=False)
        c_b = RUTMConfiguration(current_state="q1", tape={0: "1"}, head_pos=0, history=(), step_count=0, halted=False)
        colliding_domain = FiniteDomainContract(domain=[c_a, c_b], execution_horizon=1)
        bad_state_map = {"q0": 0, "q1": 0, "q_halt": 2}  # maps q0 and q1 both to 0

        with self.assertRaises(Exception):
            build_classical_semantic_model(
                self.program, colliding_domain, bad_state_map, self.symbol_map
            )


if __name__ == "__main__":
    unittest.main()
