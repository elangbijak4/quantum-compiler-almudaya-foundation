r"""
Module 3 Stage 3 Test Suite — QTM Operational Semantics & Unitary Operator Formulation.

Verifies:
1. Basis-state forward evolution U_P |C_R⟩ = |R_P(C_R)⟩
2. Superposition evolution U_P Σ α_C |C_R⟩ = Σ α_C |R_P(C_R)⟩
3. Complex superposition evolution (amplitudes with non-zero imaginary parts)
4. Linearity U_P(a|ψ⟩ + b|φ⟩) = a U_P|ψ⟩ + b U_P|φ⟩
5. Basis orthogonality preservation ⟨U_P C_1 | U_P C_2⟩ = 0
6. Norm preservation ||U_P |ψ⟩|| = |||ψ⟩||
7. Inner-product preservation ⟨U_P ψ | U_P φ⟩ = ⟨ψ | φ⟩
8. Adjoint / inverse evolution U_P† |R_P(C)⟩ = |C⟩
9. Forward/reverse round trip U_P† U_P |ψ⟩ = |ψ⟩ and U_P U_P† |ψ⟩ = |ψ⟩
10. Central correspondence U_P ∘ ι = ι ∘ R_P
11. Finite transition-closed domain operator & matrix representation [U_P]† [U_P] = I
12. Rejection of non-bijective transition mappings
13. Halting fixed-point behavior U_P |C_halt⟩ = |C_halt⟩
14. Error fixed-point behavior U_P |C_err⟩ = |C_err⟩
15. Identity extension over complementary domain C_R \ D
"""

import unittest
import math
from src.module1.utm.model import Direction, UTMProgram, TransitionAction
from src.module2.rutm.model import (
    RUTMConfiguration,
    HistoryRecord,
    create_initial_rutm_configuration,
)
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module3.qtm.basis import QuantumBasisState, iota, basis_inner_product
from src.module3.qtm.state import QTMStateVector, DEFAULT_TOLERANCE
from src.module3.qtm.operator import (
    LiftedUnitaryOperator,
    PermutationMatrixRepresentation,
    create_unitary_operator_from_program,
    create_unitary_operator_from_mapping,
)


class TestStage3UnitaryOperator(unittest.TestCase):
    """Unit test suite for Module 3 Stage 3 lifted unitary transition operators."""

    def setUp(self) -> None:
        """Sets up test UTM program and RUTM configurations."""
        self.program = UTMProgram(
            states={"q_start", "q_step1", "q_halt"},
            alphabet={"_", "0", "1"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q_step1", "1", Direction.RIGHT),
                ("q_start", "1"): TransitionAction("q_step1", "0", Direction.RIGHT),
                ("q_step1", "0"): TransitionAction("q_halt", "0", Direction.STAY),
                ("q_step1", "1"): TransitionAction("q_halt", "1", Direction.STAY),
            },
        )

        self.c0 = create_initial_rutm_configuration({0: "0", 1: "1"}, initial_state="q_start")
        self.b0 = iota(self.c0)

        self.c1 = forward_step_rutm(self.c0, self.program)
        self.b1 = iota(self.c1)

        self.c2 = forward_step_rutm(self.c1, self.program)
        self.b2 = iota(self.c2)

        self.operator = create_unitary_operator_from_program(self.program)

    def test_01_basis_forward_evolution(self) -> None:
        """Test basis-state forward evolution U_P |C_0⟩ = |R_P(C_0)⟩ = |C_1⟩."""
        target_b = self.operator.apply_basis(self.b0)
        self.assertEqual(target_b, self.b1)

        target_b1 = self.operator.apply_basis(self.b1)
        self.assertEqual(target_b1, self.b2)

    def test_02_superposition_evolution(self) -> None:
        """Test linear superposition evolution U_P (α_0|C_0⟩ + α_1|C_1⟩) = α_0|C_1⟩ + α_1|C_2⟩."""
        v_in = QTMStateVector({self.b0: 0.6, self.b1: 0.8})
        v_out = self.operator.apply_state(v_in)

        self.assertEqual(v_out.dimension, 2)
        self.assertAlmostEqual(v_out.get_amplitude(self.b1), 0.6)
        self.assertAlmostEqual(v_out.get_amplitude(self.b2), 0.8)
        self.assertAlmostEqual(v_out.norm(), 1.0)
        self.assertTrue(v_out.is_normalized())

    def test_03_complex_superposition_evolution(self) -> None:
        """Test evolution of superpositions with complex phase amplitudes."""
        amp0 = 1.0 / math.sqrt(2.0)
        amp1 = 1j / math.sqrt(2.0)

        v_in = QTMStateVector({self.b0: amp0, self.b1: amp1})
        v_out = self.operator.apply_state(v_in)

        self.assertEqual(v_out.dimension, 2)
        self.assertAlmostEqual(v_out.get_amplitude(self.b1), amp0)
        self.assertAlmostEqual(v_out.get_amplitude(self.b2), amp1)
        self.assertAlmostEqual(v_out.norm(), 1.0)

    def test_04_operator_linearity(self) -> None:
        """Test linearity U_P(a|ψ⟩ + b|φ⟩) = a U_P|ψ⟩ + b U_P|φ⟩."""
        psi = QTMStateVector({self.b0: 0.6})
        phi = QTMStateVector({self.b1: 0.8j})
        a = 2.0 + 1j
        b = -1.5

        left = self.operator.apply_state((a * psi) + (b * phi))
        right = (a * self.operator.apply_state(psi)) + (b * self.operator.apply_state(phi))

        self.assertEqual(left, right)

    def test_05_basis_orthogonality_preservation(self) -> None:
        """Test that U_P preserves orthogonality: ⟨U_P C_0 | U_P C_1⟩ = 0."""
        target_b0 = self.operator.apply_basis(self.b0)
        target_b1 = self.operator.apply_basis(self.b1)

        self.assertNotEqual(target_b0, target_b1)
        ip = basis_inner_product(target_b0, target_b1)
        self.assertEqual(ip, 0.0 + 0.0j)

    def test_06_norm_preservation(self) -> None:
        """Test norm preservation ||U_P |ψ⟩|| = |||ψ⟩|| for normalized and non-normalized states."""
        psi_norm = QTMStateVector({self.b0: 3.0 / 5.0, self.b1: 4.0 / 5.0})
        evolved_norm = self.operator.apply_state(psi_norm)
        self.assertAlmostEqual(evolved_norm.norm(), 1.0)

        psi_unnorm = QTMStateVector({self.b0: 3.0, self.b1: 4.0})
        evolved_unnorm = self.operator.apply_state(psi_unnorm)
        self.assertAlmostEqual(evolved_unnorm.norm(), 5.0)

    def test_07_inner_product_preservation(self) -> None:
        """Test inner product preservation ⟨U_P ψ | U_P φ⟩ = ⟨ψ | φ⟩."""
        psi = QTMStateVector({self.b0: 1.0 / math.sqrt(2.0), self.b1: 1j / math.sqrt(2.0)})
        phi = QTMStateVector({self.b0: 1j / math.sqrt(2.0), self.b1: 1.0 / math.sqrt(2.0)})

        ip_before = psi.inner_product(phi)
        u_psi = self.operator.apply_state(psi)
        u_phi = self.operator.apply_state(phi)
        ip_after = u_psi.inner_product(u_phi)

        self.assertAlmostEqual(ip_before.real, ip_after.real)
        self.assertAlmostEqual(ip_before.imag, ip_after.imag)

    def test_08_adjoint_inverse_evolution(self) -> None:
        """Test inverse evolution U_P† |R_P(C_0)⟩ = |C_0⟩."""
        b0_recovered = self.operator.apply_basis_adjoint(self.b1)
        self.assertEqual(b0_recovered, self.b0)

        b1_recovered = self.operator.apply_basis_adjoint(self.b2)
        self.assertEqual(b1_recovered, self.b1)

    def test_09_forward_reverse_round_trip(self) -> None:
        """Test forward/reverse round trips U_P† U_P |ψ⟩ = |ψ⟩ and U_P U_P† |ψ⟩ = |ψ⟩."""
        psi = QTMStateVector({self.b0: 0.6, self.b1: 0.8j})

        round_trip_1 = self.operator.apply_state_adjoint(self.operator.apply_state(psi))
        self.assertEqual(round_trip_1, psi)

        adj_operator = self.operator.adjoint()
        round_trip_2 = adj_operator.apply_state(self.operator.apply_state(psi))
        self.assertEqual(round_trip_2, psi)

    def test_10_central_commuting_correspondence(self) -> None:
        """Test explicit commuting correspondence: Path A (ι ∘ R_P) == Path B (U_P ∘ ι)."""
        # Path A: C_0 -> R_P(C_0) -> ι(R_P(C_0))
        c0_next = forward_step_rutm(self.c0, self.program)
        path_a = iota(c0_next)

        # Path B: C_0 -> ι(C_0) -> U_P(ι(C_0))
        path_b = self.operator.apply_basis(self.b0)

        self.assertEqual(path_a, path_b)

    def test_11_finite_3_cycle_domain_unitarity(self) -> None:
        """Test 3-cycle finite transition-closed domain (C0 -> C1 -> C2 -> C0) unitarity."""
        # Create explicit 3-cycle mapping
        mapping = {self.b0: self.b1, self.b1: self.b2, self.b2: self.b0}
        u_cycle = create_unitary_operator_from_mapping(mapping)

        domain = {self.b0, self.b1, self.b2}
        is_bijective, err_bij = u_cycle.verify_bijectivity(domain)
        self.assertTrue(is_bijective, msg=err_bij)

        is_unitary, err_u = u_cycle.verify_unitarity(domain)
        self.assertTrue(is_unitary, msg=err_u)

        # Matrix representation test [U_P]† [U_P] = I and [U_P] [U_P]† = I
        matrix_rep = u_cycle.get_permutation_matrix([self.b0, self.b1, self.b2])
        self.assertEqual(matrix_rep.size, 3)
        self.assertTrue(matrix_rep.is_permutation())
        self.assertTrue(matrix_rep.is_unitary())

    def test_12_rejection_of_non_bijective_mapping(self) -> None:
        """Test negative verification: Reject non-bijective transition mappings (collisions)."""
        # Non-bijective collision: both b0 and b1 map to b2
        bad_mapping = {self.b0: self.b2, self.b1: self.b2, self.b2: self.b0}

        with self.assertRaises(ValueError) as ctx:
            create_unitary_operator_from_mapping(bad_mapping)
        self.assertIn("Non-bijective mapping", str(ctx.exception))

    def test_13_halting_fixed_point_behavior(self) -> None:
        """Test halting terminal state fixed-point evolution U_P |C_halt⟩ = |C_halt⟩ under bijectivity."""
        # c2 is halted
        self.assertTrue(self.c2.halted)

        target_halt = self.operator.apply_basis(self.b2)
        self.assertEqual(target_halt, self.b2)
        self.assertTrue(target_halt.config.halted)

    def test_14_error_fixed_point_behavior(self) -> None:
        """Test error terminal state fixed-point evolution U_P |C_err⟩ = |C_err⟩ under bijectivity."""
        c_err = RUTMConfiguration(
            current_state="q_start",
            tape={0: "0"},
            head_pos=0,
            history=(),
            step_count=0,
            halted=False,
            error="Test runtime error",
        )
        b_err = iota(c_err)

        target_err = self.operator.apply_basis(b_err)
        self.assertEqual(target_err, b_err)
        self.assertEqual(target_err.config.error, "Test runtime error")

    def test_15_identity_extension_unmapped_configurations(self) -> None:
        """Test Audit C: Identity extension R_P(C) = C on unmapped configurations outside explicit domain D."""
        mapping = {self.b0: self.b1, self.b1: self.b0}
        u = create_unitary_operator_from_mapping(mapping)

        # Unmapped basis state outside D
        c_unmapped = create_initial_rutm_configuration({99: "1"}, initial_state="q_other")
        b_unmapped = iota(c_unmapped)

        # Forward identity R_P(C) = C
        self.assertEqual(u.apply_basis(b_unmapped), b_unmapped)

        # Reverse identity R_P^{-1}(C) = C
        self.assertEqual(u.apply_basis_adjoint(b_unmapped), b_unmapped)


if __name__ == "__main__":
    unittest.main()
