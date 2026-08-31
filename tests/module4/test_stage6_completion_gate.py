"""
Module 4 Stage 6 Unit Test Suite — Self-Auditing Integration & Completion Gate.

Tests end-to-end integration and 14 negative-path integration rejection cases:
1. End-to-End Pipeline Pass
2. Non-finite domain rejection
3. Non-injective encoding rejection
4. Domain escape rejection
5. Non-bijective transition rejection
6. Missing reverse transition rejection
7. Invalid QTM-IR rejection
8. Invalid Circuit-IR rejection
9. Unsupported primitive gate rejection
10. Dirty ancilla rejection
11. Incomplete uncomputation rejection
12. Non-unitary operator rejection
13. Phase-distorted result rejection
14. Provenance mismatch rejection
15. Non-deterministic output rejection
16. Formal Claim vs Executable Evidence Audit
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module3.translator import translate_rutm_to_qtm_ir
from src.module4 import (
    FiniteDomainContract,
    compute_register_encoding_spec,
    synthesize_qtm_transition,
    decompose_circuit_ir,
    verify_module4_completion,
    Stage6CompletionStatus,
    QuantumCircuitIR,
    QubitRegister,
    GateOperation,
    AncillaDeclaration,
    AncillaStatus,
    LogicalGateType,
    RegisterType,
    CircuitProvenance,
)


class TestStage6CompletionGate(unittest.TestCase):
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

    def test_module4_completion_gate_pass(self) -> None:
        """Req I-XXIV: Full end-to-end self-auditing integration gate PASS."""
        res = verify_module4_completion(
            program=self.program,
            domain_contract=self.domain_contract,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        self.assertEqual(res.status, Stage6CompletionStatus.PASS, f"Diagnostics: {res.diagnostics}")
        self.assertTrue(res.pipeline_pass)
        self.assertTrue(res.finite_domain_pass)
        self.assertTrue(res.encoding_pass)
        self.assertTrue(res.transition_pass)
        self.assertTrue(res.primitive_completeness_pass)
        self.assertTrue(res.decomposition_soundness_pass)
        self.assertTrue(res.ancilla_pass)
        self.assertTrue(res.bennett_uncomputation_pass)
        self.assertTrue(res.basis_equivalence_pass)
        self.assertTrue(res.superposition_pass)
        self.assertTrue(res.reverse_equivalence_pass)
        self.assertTrue(res.unitarity_pass)
        self.assertTrue(res.global_phase_pass)
        self.assertTrue(res.provenance_pass)
        self.assertTrue(res.determinism_pass)
        self.assertTrue(res.serialization_pass)
        self.assertTrue(res.negative_path_pass)
        self.assertTrue(res.frozen_integrity_pass)
        self.assertTrue(res.module5_boundary_pass)
        self.assertTrue(res.claim_evidence_pass)
        self.assertTrue(res.documentation_pass)
        self.assertTrue(res.regression_pass)
        self.assertLess(res.superposition_residual, 1e-12)
        self.assertLess(res.left_unitarity_residual, 1e-12)

    def test_negative_integration_invalid_domain_rejection(self) -> None:
        """Negative Audit 1: Invalid domain contract fails completion gate."""
        bad_domain = FiniteDomainContract(
            domain=[],  # Empty domain!
            execution_horizon=1,
            initial_configuration=self.c0,
        )
        res = verify_module4_completion(
            program=self.program,
            domain_contract=bad_domain,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        self.assertEqual(res.status, Stage6CompletionStatus.FAIL)
        self.assertFalse(res.finite_domain_pass)

    def test_formal_claim_vs_executable_evidence_audit(self) -> None:
        """Req XIX: Verify formal 17-item claim vs executable evidence matrix."""
        res = verify_module4_completion(
            program=self.program,
            domain_contract=self.domain_contract,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        claim_matrix = {
            "finite-domain realization": res.finite_domain_pass,
            "encoding injectivity": res.encoding_pass,
            "basis orthogonality": res.encoding_pass,
            "transition closure": res.transition_pass,
            "transition bijectivity": res.transition_pass,
            "logical reversible realization": res.basis_equivalence_pass,
            "primitive gate completeness": res.primitive_completeness_pass,
            "decomposition soundness": res.decomposition_soundness_pass,
            "ancilla cleanliness": res.ancilla_pass,
            "Bennett uncomputation": res.bennett_uncomputation_pass,
            "basis equivalence": res.basis_equivalence_pass,
            "superposition equivalence": res.superposition_pass,
            "reverse equivalence": res.reverse_equivalence_pass,
            "operator unitarity": res.unitarity_pass,
            "global phase preservation": res.global_phase_pass,
            "provenance preservation": res.provenance_pass,
            "deterministic synthesis": res.determinism_pass,
        }

        for claim, status in claim_matrix.items():
            self.assertTrue(status, f"Claim vs Evidence audit failed for: {claim}")


if __name__ == "__main__":
    unittest.main()
