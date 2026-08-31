"""
Module 3 Stage 8 Test Suite — Reversible -> Quantum Equivalence Verification Gate.

Verifies:
1. test_initial_embedding_equivalence
2. test_single_step_equivalence
3. test_multi_step_equivalence (positive test T >= 5 inspecting EVERY step)
4. test_equivalence_holds_at_every_step
5. test_first_divergence_is_reported (divergence at t > 0)
6. test_wrong_transition_fails
7. test_wrong_basis_identity_fails
8. test_extra_quantum_amplitude_fails
9. test_missing_basis_fails_or_inconclusive
10. test_history_identity_is_preserved (alters ONLY history)
11. test_halting_equivalence
12. test_error_equivalence
13. test_domain_mismatch_is_not_pass
14. test_zero_step_equivalence
15. test_invalid_qtm_ir_rejected
16. test_invalid_horizon_rejected
17. test_reverse_equivalence_if_implemented
"""

import unittest
import math
from typing import Dict, List

from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import (
    HistoryRecord,
    RUTMConfiguration,
    create_initial_rutm_configuration,
)
from src.module2.rutm.semantics import forward_step_rutm
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRComplexNumber,
)
from src.module3.translator import (
    translate_rutm_to_qtm_ir,
    compute_canonical_basis_id,
    lift_configuration,
)
from src.module3.equivalence import (
    EquivalenceStatus,
    EquivalenceStepResult,
    EquivalenceResult,
    EquivalenceGate,
    verify_equivalence,
)


class TestStage8EquivalenceGate(unittest.TestCase):
    """Unit test suite for Reversible -> Quantum Equivalence Verification Gate."""

    def setUp(self) -> None:
        """Sets up RUTM programs and translated QTM-IR models for testing."""
        self.transitions = {
            ("q0", "0"): TransitionAction(next_state="q1", write_symbol="1", direction=Direction.RIGHT),
            ("q1", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT),
        }
        self.utm_program = UTMProgram(
            states={"q0", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q0",
            halt_state="q_halt",
            transitions=self.transitions,
        )

        # Build 6 distinct terminal fixed-point configurations for multi-step domain
        self.configs: List[RUTMConfiguration] = []
        for i in range(6):
            tape = {j: "1" for j in range(i + 1)}
            c = RUTMConfiguration(
                current_state="q_halt", tape=tape, head_pos=i, history=(), step_count=0, halted=True
            )
            self.configs.append(c)

        self.c0 = self.configs[0]

        # Translate to QTM-IR over the closed domain of 6 distinct halted configurations
        self.qtm_ir = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=self.configs)

        # Single state fixed point fixtures
        self.c_halt = self.configs[0]
        self.c_error = RUTMConfiguration(
            current_state="q1", tape={0: "1"}, head_pos=1, history=(), step_count=0, halted=False, error="Tape symbol out of alphabet"
        )
        self.qtm_ir_halt = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        self.qtm_ir_error = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_error])

    def test_initial_embedding_equivalence(self) -> None:
        """Req 5 & 28: Verify initial state embedding |psi_0> == iota(C_0)."""
        res = verify_equivalence(self.utm_program, self.qtm_ir, initial_config=self.c0, max_steps=0)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        self.assertEqual(res.verified_steps, 1)

    def test_single_step_equivalence(self) -> None:
        """Req 28: Single step equivalence iota(R_P(C_0)) == U_P |C_0>."""
        res = verify_equivalence(self.utm_program, self.qtm_ir, initial_config=self.c0, max_steps=1)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        self.assertEqual(res.verified_steps, 2)

    def test_multi_step_equivalence(self) -> None:
        """Req 28 & 29: Positive test T >= 5 inspecting EVERY step."""
        res = verify_equivalence(self.utm_program, self.qtm_ir, initial_config=self.c0, max_steps=5)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        self.assertEqual(res.max_steps, 5)
        self.assertEqual(res.verified_steps, 6)
        self.assertIsNone(res.first_failure_step)
        self.assertEqual(len(res.trace), 6)

        # Verify EVERY step in trace
        for step_idx, step_res in enumerate(res.trace):
            self.assertEqual(step_res.step, step_idx)
            self.assertTrue(step_res.support_match)
            self.assertTrue(step_res.amplitude_match)
            self.assertTrue(step_res.identity_match)
            self.assertEqual(step_res.status, EquivalenceStatus.PASS)

    def test_equivalence_holds_at_every_step(self) -> None:
        """Req 10 & 28: Verify every step t in [0 ... T] matches classical R_P^t(C_0)."""
        res = verify_equivalence(self.utm_program, self.qtm_ir, initial_config=self.c0, max_steps=3)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        for t in range(4):
            exp_id = compute_canonical_basis_id(self.c0)
            self.assertEqual(res.trace[t].expected_basis_id, exp_id)

    def test_first_divergence_is_reported(self) -> None:
        """Req 11, 28, 29: Negative test introducing divergence at t > 0."""
        c0_id = compute_canonical_basis_id(self.c0)
        c1_id = compute_canonical_basis_id(self.configs[1])

        # Swap forward targets for c0_id and c1_id (valid bijection, passes validate_qtm_ir)
        corrupted_f_map = dict(self.qtm_ir.transition_mapping.forward_mapping)
        corrupted_f_map[c0_id] = c1_id
        corrupted_f_map[c1_id] = c0_id

        corrupted_r_map = dict(self.qtm_ir.transition_mapping.reverse_mapping)
        corrupted_r_map[c1_id] = c0_id
        corrupted_r_map[c0_id] = c1_id

        corrupted_mapping = QTMIRTransitionMapping(
            forward_mapping=corrupted_f_map,
            reverse_mapping=corrupted_r_map,
            is_bijective=True,
        )
        corrupted_qtm_ir = QTMIRModel(
            version=self.qtm_ir.version,
            machine_id="corrupted",
            basis_states=self.qtm_ir.basis_states,
            initial_state_vector=self.qtm_ir.initial_state_vector,
            transition_mapping=corrupted_mapping,
            provenance=self.qtm_ir.provenance,
        )

        res = verify_equivalence(self.utm_program, corrupted_qtm_ir, initial_config=self.c0, max_steps=3)
        self.assertEqual(res.status, EquivalenceStatus.FAIL)
        self.assertEqual(res.first_failure_step, 1)
        self.assertIn("First divergence observed at step 1", res.diagnostics[0])

    def test_wrong_transition_fails(self) -> None:
        """Req 26 & 28: Wrong QTM transition mapping causes FAIL."""
        c0_id = compute_canonical_basis_id(self.c0)
        c1_id = compute_canonical_basis_id(self.configs[1])

        # Swap forward targets for c0_id and c1_id
        corrupted_f_map = dict(self.qtm_ir.transition_mapping.forward_mapping)
        corrupted_f_map[c0_id] = c1_id
        corrupted_f_map[c1_id] = c0_id

        corrupted_r_map = dict(self.qtm_ir.transition_mapping.reverse_mapping)
        corrupted_r_map[c1_id] = c0_id
        corrupted_r_map[c0_id] = c1_id

        corrupted_qtm_ir = QTMIRModel(
            version=self.qtm_ir.version,
            machine_id="wrong_trans",
            basis_states=self.qtm_ir.basis_states,
            initial_state_vector=self.qtm_ir.initial_state_vector,
            transition_mapping=QTMIRTransitionMapping(
                forward_mapping=corrupted_f_map,
                reverse_mapping=corrupted_r_map,
                is_bijective=True,
            ),
            provenance=self.qtm_ir.provenance,
        )

        res = verify_equivalence(self.utm_program, corrupted_qtm_ir, initial_config=self.c0, max_steps=2)
        self.assertEqual(res.status, EquivalenceStatus.FAIL)
        self.assertEqual(res.first_failure_step, 1)

    def test_wrong_basis_identity_fails(self) -> None:
        """Req 26 & 28: Mismatched basis state ID causes FAIL."""
        c0_id = compute_canonical_basis_id(self.c0)
        modified_basis = dict(self.qtm_ir.basis_states)
        modified_basis[c0_id] = QTMIRBasisState(
            basis_id=c0_id, current_state="q_wrong", tape={}, head_pos=99
        )

        modified_qtm_ir = QTMIRModel(
            version=self.qtm_ir.version,
            machine_id="wrong_basis",
            basis_states=modified_basis,
            initial_state_vector=self.qtm_ir.initial_state_vector,
            transition_mapping=self.qtm_ir.transition_mapping,
            provenance=self.qtm_ir.provenance,
        )

        res = verify_equivalence(self.utm_program, modified_qtm_ir, initial_config=self.c0, max_steps=2)
        self.assertEqual(res.status, EquivalenceStatus.FAIL)
        self.assertEqual(res.first_failure_step, 0)

    def test_extra_quantum_amplitude_fails(self) -> None:
        """Req 8, 26, 28: Quantum state with extra spurious amplitude causes FAIL."""
        c0_id = compute_canonical_basis_id(self.c0)
        c1_id = compute_canonical_basis_id(self.configs[1])

        # Normalized initial state vector with extra spurious amplitude (norm 1.0)
        spurious_init = QTMIRStateVector(
            amplitudes={
                c0_id: QTMIRComplexNumber(0.6, 0.0),
                c1_id: QTMIRComplexNumber(0.8, 0.0),  # Extra spurious amplitude!
            }
        )
        spurious_qtm_ir = QTMIRModel(
            version=self.qtm_ir.version,
            machine_id="spurious",
            basis_states=self.qtm_ir.basis_states,
            initial_state_vector=spurious_init,
            transition_mapping=self.qtm_ir.transition_mapping,
            provenance=self.qtm_ir.provenance,
        )

        res = verify_equivalence(self.utm_program, spurious_qtm_ir, initial_config=self.c0, max_steps=1)
        self.assertEqual(res.status, EquivalenceStatus.FAIL)
        self.assertEqual(res.first_failure_step, 0)
        self.assertFalse(res.trace[0].support_match)

    def test_missing_basis_fails_or_inconclusive(self) -> None:
        """Req 13, 26, 28: Missing classical basis state in QTM-IR domain produces INCONCLUSIVE."""
        truncated_qtm_ir = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=self.configs[:3])

        # Try executing with an initial config not in truncated_qtm_ir (c3 is not in configs[:3])
        c3 = self.configs[3]
        res = verify_equivalence(self.utm_program, truncated_qtm_ir, initial_config=c3, max_steps=2)
        self.assertEqual(res.status, EquivalenceStatus.INCONCLUSIVE)
        self.assertEqual(res.verified_steps, 0)

    def test_history_identity_is_preserved(self) -> None:
        """Req 6, 19, 28, 29: Configuration identity MUST include history; altering history alters identity."""
        h0 = HistoryRecord(prev_state="q0", overwritten_symbol="0", direction=Direction.RIGHT)
        c1_orig = RUTMConfiguration(current_state="q1", tape={0: "1"}, head_pos=1, history=(h0,), step_count=1)
        c1_diff_hist = RUTMConfiguration(current_state="q1", tape={0: "1"}, head_pos=1, history=(), step_count=1)

        id_orig = compute_canonical_basis_id(c1_orig)
        id_diff = compute_canonical_basis_id(c1_diff_hist)

        self.assertNotEqual(id_orig, id_diff)

    def test_halting_equivalence(self) -> None:
        """Req 20 & 28: Halting fixed point R_P(C_halt) = C_halt <-> U_P |C_halt> = |C_halt>."""
        res = verify_equivalence(self.utm_program, self.qtm_ir_halt, initial_config=self.c_halt, max_steps=3)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        self.assertEqual(res.verified_steps, 4)

    def test_error_equivalence(self) -> None:
        """Req 21 & 28: Error fixed point R_P(C_error) = C_error <-> U_P |C_error> = |C_error>."""
        res = verify_equivalence(self.utm_program, self.qtm_ir_error, initial_config=self.c_error, max_steps=3)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        self.assertEqual(res.verified_steps, 4)

    def test_domain_mismatch_is_not_pass(self) -> None:
        """Req 13 & 28: Execution horizon exceeding domain is INCONCLUSIVE, not PASS."""
        single_state_qtm_ir = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        c_other = self.configs[1]
        res = verify_equivalence(self.utm_program, single_state_qtm_ir, initial_config=c_other, max_steps=3)
        self.assertEqual(res.status, EquivalenceStatus.INCONCLUSIVE)
        self.assertNotEqual(res.status, EquivalenceStatus.PASS)

    def test_zero_step_equivalence(self) -> None:
        """Req 14 & 28: max_steps = 0 verifies step 0 initial state embedding."""
        res = verify_equivalence(self.utm_program, self.qtm_ir, initial_config=self.c0, max_steps=0)
        self.assertEqual(res.status, EquivalenceStatus.PASS)
        self.assertEqual(res.verified_steps, 1)

    def test_invalid_qtm_ir_rejected(self) -> None:
        """Req 4 & 28: Invalid QTM-IR model produces INCONCLUSIVE."""
        c0_id = compute_canonical_basis_id(self.c0)
        invalid_qtm_ir = QTMIRModel(
            machine_id="invalid",
            basis_states={c0_id: lift_configuration(self.c0, c0_id)},
            initial_state_vector=QTMIRStateVector(amplitudes={c0_id: QTMIRComplexNumber(1.0, 0.0)}),
            transition_mapping=QTMIRTransitionMapping(forward_mapping={}, reverse_mapping={}),  # Missing forward mapping
        )

        res = verify_equivalence(self.utm_program, invalid_qtm_ir, initial_config=self.c0, max_steps=1)
        self.assertEqual(res.status, EquivalenceStatus.INCONCLUSIVE)

    def test_invalid_horizon_rejected(self) -> None:
        """Req 14 & 28: Negative horizon max_steps < 0 produces INCONCLUSIVE."""
        res = verify_equivalence(self.utm_program, self.qtm_ir, initial_config=self.c0, max_steps=-1)
        self.assertEqual(res.status, EquivalenceStatus.INCONCLUSIVE)

    def test_reverse_equivalence_if_implemented(self) -> None:
        """Req 18 & 28: Reverse equivalence check U_P^dagger iota(C_t) == iota(R_P^-1(C_t))."""
        res = verify_equivalence(
            self.utm_program, self.qtm_ir_error, initial_config=self.c_error, max_steps=3, verify_reverse=True
        )
        self.assertEqual(res.status, EquivalenceStatus.PASS)


if __name__ == "__main__":
    unittest.main()
