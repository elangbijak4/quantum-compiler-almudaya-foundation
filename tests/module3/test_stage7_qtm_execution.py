"""
Module 3 Stage 7 Test Suite — QTM Execution Engine & State Vector Evolution.

Verifies:
1. test_valid_qtm_ir_execution
2. test_basis_state_evolution_matches_transition_mapping
3. test_superposition_evolution
4. test_complex_amplitude_evolution
5. test_unitary_evolution_linearity
6. test_norm_preservation_under_execution
7. test_inner_product_preservation
8. test_adjoint_execution
9. test_adjoint_forward_round_trip
10. test_execution_trace_consistency
11. test_zero_step_execution
12. test_multi_step_execution
13. test_halting_basis_state_fixed_point
14. test_error_basis_state_fixed_point
15. test_mapping_and_matrix_execution_agree
16. test_invalid_qtm_ir_rejected
17. test_unknown_basis_state_rejected
18. test_missing_transition_rejected
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
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    CANONICAL_SEMANTIC_RELATION,
)
from src.module3.translator import (
    translate_rutm_to_qtm_ir,
    compute_canonical_basis_id,
    lift_configuration,
)
from src.module3.execution import (
    QTMExecutionError,
    QTMExecutionTrace,
    QTMExecutionEngine,
    apply_unitary,
    apply_adjoint,
    apply_matrix,
    execute,
    execute_matrix,
    normalize_state,
    inner_product,
)


class TestStage7QTMExecution(unittest.TestCase):
    """Unit test suite for QTM Execution Engine & State Vector Evolution."""

    def setUp(self) -> None:
        """Sets up test RUTM programs and QTM-IR models for execution."""
        # Simple reversible 2-step program
        self.transitions = {
            ("q_start", "0"): TransitionAction(next_state="q_step1", write_symbol="1", direction=Direction.RIGHT),
            ("q_step1", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT),
        }
        self.utm_program = UTMProgram(
            states={"q_start", "q_step1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions=self.transitions,
        )

        # Single terminal fixed point configuration
        self.c_halt = RUTMConfiguration(
            current_state="q_halt", tape={0: "1", 1: "1"}, head_pos=2, history=(), step_count=0, halted=True
        )

        # Single error fixed point configuration
        self.c_error = RUTMConfiguration(
            current_state="q_step1", tape={0: "1"}, head_pos=1, history=(), step_count=0, halted=False, error="Tape symbol out of alphabet"
        )

        # 2-state custom domain for superposition tests: b0 (c_halt) and b1 (c_error)
        self.b0_id = compute_canonical_basis_id(self.c_halt)
        self.b1_id = compute_canonical_basis_id(self.c_error)

        self.model_2state = translate_rutm_to_qtm_ir(
            self.utm_program, custom_domain=[self.c_halt, self.c_error], include_matrix=True
        )

        # Single state model
        self.model_halt = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt], include_matrix=True)
        self.model_error = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_error], include_matrix=True)

    def test_valid_qtm_ir_execution(self) -> None:
        """Req 1 & 31: Valid QTM-IR execution produces a valid QTMExecutionTrace."""
        trace = execute(self.model_halt, steps=2)
        self.assertIsInstance(trace, QTMExecutionTrace)
        self.assertEqual(trace.step_count, 2)
        self.assertEqual(len(trace.states), 3)
        self.assertEqual(len(trace.norm_trace), 3)
        self.assertTrue(trace.halted)

    def test_basis_state_evolution_matches_transition_mapping(self) -> None:
        """Req 9 & 31: Basis-state evolution apply_unitary(|C>) matches forward transition mapping."""
        b_state_vector = QTMIRStateVector(
            amplitudes={self.b0_id: QTMIRComplexNumber(1.0, 0.0)}
        )
        next_state = apply_unitary(self.model_2state, b_state_vector)

        expected_tgt_id = self.model_2state.transition_mapping.forward_mapping[self.b0_id]
        self.assertIn(expected_tgt_id, next_state.amplitudes)
        self.assertAlmostEqual(next_state.amplitudes[expected_tgt_id].real, 1.0)
        self.assertAlmostEqual(next_state.amplitudes[expected_tgt_id].imag, 0.0)

    def test_superposition_evolution(self) -> None:
        """Req 10 & 31: Real superposition evolution U_P (alpha|C1> + beta|C2>)."""
        alpha = 1.0 / math.sqrt(2.0)
        beta = 1.0 / math.sqrt(2.0)
        sup_state = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(alpha, 0.0),
                self.b1_id: QTMIRComplexNumber(beta, 0.0),
            }
        )

        out_state = apply_unitary(self.model_2state, sup_state)
        tgt0 = self.model_2state.transition_mapping.forward_mapping[self.b0_id]
        tgt1 = self.model_2state.transition_mapping.forward_mapping[self.b1_id]

        self.assertAlmostEqual(out_state.amplitudes[tgt0].real, alpha)
        self.assertAlmostEqual(out_state.amplitudes[tgt1].real, beta)
        self.assertAlmostEqual(out_state.compute_norm(), 1.0)

    def test_complex_amplitude_evolution(self) -> None:
        """Req 10 & 31: Complex superposition evolution (alpha = 1/sqrt(2), beta = i/sqrt(2))."""
        alpha = 1.0 / math.sqrt(2.0)
        beta = 1.0 / math.sqrt(2.0)
        complex_state = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(alpha, 0.0),
                self.b1_id: QTMIRComplexNumber(0.0, beta),  # i / sqrt(2)
            }
        )

        out_state = apply_unitary(self.model_2state, complex_state)
        tgt0 = self.model_2state.transition_mapping.forward_mapping[self.b0_id]
        tgt1 = self.model_2state.transition_mapping.forward_mapping[self.b1_id]

        self.assertAlmostEqual(out_state.amplitudes[tgt0].real, alpha)
        self.assertAlmostEqual(out_state.amplitudes[tgt0].imag, 0.0)
        self.assertAlmostEqual(out_state.amplitudes[tgt1].real, 0.0)
        self.assertAlmostEqual(out_state.amplitudes[tgt1].imag, beta)
        self.assertAlmostEqual(out_state.compute_norm(), 1.0)

    def test_unitary_evolution_linearity(self) -> None:
        """Req 8 & 31: Linearity verification U_P(alpha|psi> + beta|phi>) = alpha U_P|psi> + beta U_P|phi>."""
        psi = QTMIRStateVector(amplitudes={self.b0_id: QTMIRComplexNumber(1.0, 0.0)})
        phi = QTMIRStateVector(amplitudes={self.b1_id: QTMIRComplexNumber(0.0, 1.0)})

        c_a = 0.6
        c_b = 0.8

        # Left side: U_P(0.6|psi> + 0.8|phi>)
        combined_amps = {
            self.b0_id: QTMIRComplexNumber(c_a, 0.0),
            self.b1_id: QTMIRComplexNumber(0.0, c_b),
        }
        lhs = apply_unitary(self.model_2state, QTMIRStateVector(amplitudes=combined_amps))

        # Right side: 0.6 U_P|psi> + 0.8 U_P|phi>
        u_psi = apply_unitary(self.model_2state, psi)
        u_phi = apply_unitary(self.model_2state, phi)

        tgt0 = self.model_2state.transition_mapping.forward_mapping[self.b0_id]
        tgt1 = self.model_2state.transition_mapping.forward_mapping[self.b1_id]

        self.assertAlmostEqual(lhs.amplitudes[tgt0].real, c_a * u_psi.amplitudes[tgt0].real)
        self.assertAlmostEqual(lhs.amplitudes[tgt1].imag, c_b * u_phi.amplitudes[tgt1].imag)

    def test_norm_preservation_under_execution(self) -> None:
        """Req 11 & 31: Multi-step norm preservation ||psi(t+1)|| = ||psi(t)|| = 1.0."""
        sup_state = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(0.6, 0.0),
                self.b1_id: QTMIRComplexNumber(0.0, 0.8),
            }
        )
        trace = execute(self.model_2state, initial_state=sup_state, steps=5)

        for norm_val in trace.norm_trace:
            self.assertAlmostEqual(norm_val, 1.0, places=10)

    def test_inner_product_preservation(self) -> None:
        """Req 12 & 31: Inner product preservation <U_P psi | U_P phi> = <psi | phi>."""
        psi = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(1.0 / math.sqrt(2.0), 0.0),
                self.b1_id: QTMIRComplexNumber(0.0, 1.0 / math.sqrt(2.0)),
            }
        )
        phi = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(0.6, 0.0),
                self.b1_id: QTMIRComplexNumber(0.8, 0.0),
            }
        )

        ip_before = inner_product(psi, phi)

        u_psi = apply_unitary(self.model_2state, psi)
        u_phi = apply_unitary(self.model_2state, phi)
        ip_after = inner_product(u_psi, u_phi)

        self.assertAlmostEqual(ip_before.real, ip_after.real, places=10)
        self.assertAlmostEqual(ip_before.imag, ip_after.imag, places=10)

    def test_adjoint_execution(self) -> None:
        """Req 13 & 31: Adjoint operator execution U_P^dagger using reverse mapping."""
        sup_state = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(0.6, 0.0),
                self.b1_id: QTMIRComplexNumber(0.0, 0.8),
            }
        )
        adj_state = apply_adjoint(self.model_2state, sup_state)

        rev0 = self.model_2state.transition_mapping.reverse_mapping[self.b0_id]
        rev1 = self.model_2state.transition_mapping.reverse_mapping[self.b1_id]

        self.assertAlmostEqual(adj_state.amplitudes[rev0].real, 0.6)
        self.assertAlmostEqual(adj_state.amplitudes[rev1].imag, 0.8)

    def test_adjoint_forward_round_trip(self) -> None:
        """Req 14 & 31: U_P^dagger U_P |psi> = |psi> and U_P U_P^dagger |psi> = |psi> round trips."""
        sup_state = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(0.6, 0.0),
                self.b1_id: QTMIRComplexNumber(0.0, 0.8),
            }
        )

        # U_P^dagger (U_P |psi>) = |psi>
        u_fwd = apply_unitary(self.model_2state, sup_state)
        u_round1 = apply_adjoint(self.model_2state, u_fwd)

        self.assertAlmostEqual(u_round1.amplitudes[self.b0_id].real, 0.6)
        self.assertAlmostEqual(u_round1.amplitudes[self.b1_id].imag, 0.8)

        # U_P (U_P^dagger |psi>) = |psi>
        u_rev = apply_adjoint(self.model_2state, sup_state)
        u_round2 = apply_unitary(self.model_2state, u_rev)

        self.assertAlmostEqual(u_round2.amplitudes[self.b0_id].real, 0.6)
        self.assertAlmostEqual(u_round2.amplitudes[self.b1_id].imag, 0.8)

    def test_execution_trace_consistency(self) -> None:
        """Req 15 & 31: Execution trace consistency trace[t+1] == apply_unitary(trace[t])."""
        trace = execute(self.model_2state, steps=3)
        for t in range(trace.step_count):
            expected_next = apply_unitary(self.model_2state, trace.states[t])
            self.assertEqual(trace.states[t + 1].amplitudes, expected_next.amplitudes)

    def test_zero_step_execution(self) -> None:
        """Req 16 & 31: execute(model, steps=0) returns final_state == initial_state and trace len == 1."""
        trace = execute(self.model_2state, steps=0)
        self.assertEqual(trace.step_count, 0)
        self.assertEqual(len(trace.states), 1)
        self.assertEqual(trace.final_state.amplitudes, trace.initial_state.amplitudes)

    def test_multi_step_execution(self) -> None:
        """Req 17 & 31: execute(model, steps=N) produces U_P^N |psi_0>."""
        N = 4
        trace = execute(self.model_2state, steps=N)

        curr = self.model_2state.initial_state_vector
        for _ in range(N):
            curr = apply_unitary(self.model_2state, curr)

        self.assertEqual(trace.final_state.amplitudes, curr.amplitudes)

    def test_halting_basis_state_fixed_point(self) -> None:
        """Req 18 & 31: Halting basis state is a unitary fixed point U_P |C_halt> = |C_halt>."""
        halt_vector = QTMIRStateVector(
            amplitudes={compute_canonical_basis_id(self.c_halt): QTMIRComplexNumber(1.0, 0.0)}
        )
        out_state = apply_unitary(self.model_halt, halt_vector)
        self.assertEqual(out_state.amplitudes, halt_vector.amplitudes)

    def test_error_basis_state_fixed_point(self) -> None:
        """Req 19 & 31: Error basis state is a unitary fixed point U_P |C_error> = |C_error>."""
        error_vector = QTMIRStateVector(
            amplitudes={compute_canonical_basis_id(self.c_error): QTMIRComplexNumber(1.0, 0.0)}
        )
        out_state = apply_unitary(self.model_error, error_vector)
        self.assertEqual(out_state.amplitudes, error_vector.amplitudes)

    def test_mapping_and_matrix_execution_agree(self) -> None:
        """Req 23 & 31: Cross-validation: apply_unitary() agrees with apply_matrix()."""
        sup_state = QTMIRStateVector(
            amplitudes={
                self.b0_id: QTMIRComplexNumber(0.6, 0.0),
                self.b1_id: QTMIRComplexNumber(0.0, 0.8),
            }
        )

        out_mapping = apply_unitary(self.model_2state, sup_state)
        out_matrix = apply_matrix(self.model_2state, sup_state)

        for b_id in self.model_2state.basis_states.keys():
            m_amp = out_mapping.amplitudes.get(b_id, QTMIRComplexNumber(0.0, 0.0)).to_complex()
            mat_amp = out_matrix.amplitudes.get(b_id, QTMIRComplexNumber(0.0, 0.0)).to_complex()
            self.assertAlmostEqual(m_amp.real, mat_amp.real, places=10)
            self.assertAlmostEqual(m_amp.imag, mat_amp.imag, places=10)

    def test_invalid_qtm_ir_rejected(self) -> None:
        """Req 25 & 31: Invalid QTM-IR model rejected before execution."""
        # Create invalid model with missing forward mapping
        invalid_model = QTMIRModel(
            machine_id="invalid",
            basis_states={self.b0_id: lift_configuration(self.c_halt, self.b0_id)},
            initial_state_vector=QTMIRStateVector(amplitudes={self.b0_id: QTMIRComplexNumber(1.0, 0.0)}),
            transition_mapping=QTMIRTransitionMapping(forward_mapping={}, reverse_mapping={}),
        )

        with self.assertRaises(QTMExecutionError):
            apply_unitary(invalid_model, invalid_model.initial_state_vector)

    def test_unknown_basis_state_rejected(self) -> None:
        """Req 26 & 31: Unknown basis ID in state vector rejected with QTMExecutionError."""
        unknown_vector = QTMIRStateVector(
            amplitudes={"unknown_basis_id_123": QTMIRComplexNumber(1.0, 0.0)}
        )
        with self.assertRaises(QTMExecutionError):
            apply_unitary(self.model_2state, unknown_vector)

    def test_missing_transition_rejected(self) -> None:
        """Req 27 & 31: Missing transition in mapping rejected with QTMExecutionError."""
        incomplete_mapping = QTMIRTransitionMapping(
            forward_mapping={self.b0_id: self.b0_id},  # b1_id missing
            reverse_mapping={self.b0_id: self.b0_id},
            is_bijective=True,
        )
        incomplete_model = QTMIRModel(
            version=self.model_2state.version,
            machine_id="incomplete",
            basis_states=self.model_2state.basis_states,
            initial_state_vector=self.model_2state.initial_state_vector,
            transition_mapping=incomplete_mapping,
            provenance=self.model_2state.provenance,
        )

        b1_vector = QTMIRStateVector(
            amplitudes={self.b1_id: QTMIRComplexNumber(1.0, 0.0)}
        )
        with self.assertRaises(QTMExecutionError):
            apply_unitary(incomplete_model, b1_vector)


if __name__ == "__main__":
    unittest.main()
