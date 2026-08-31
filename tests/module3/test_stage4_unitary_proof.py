r"""
Module 3 Stage 4 Test Suite — Executable Witnesses for Unitary Equivalence & Norm Preservation Proofs.

Serves as executable verification witnesses for the formal mathematical theorems proven in
docs/module-3/STAGE_4_UNITARY_EQUIVALENCE_PROOF.md:

1. Theorem 1 Witness: Left Unitarity U_P† U_P = I
2. Theorem 2 Witness: Right Unitarity U_P U_P† = I
3. Theorem 4 Witness: Norm Preservation ||U_P ψ|| = ||ψ||
4. Theorem 5 Witness: Inner-Product Preservation ⟨U_P ψ | U_P φ⟩ = ⟨ψ | φ⟩
5. Theorem 6 Witness: Orthonormal Basis Preservation ⟨U_P C_1 | U_P C_2⟩ = δ_(C_1, C_2)
6. Theorem 7 Witness: Forward Commuting Correspondence U_P ∘ ι = ι ∘ R_P
7. Theorem 8 Witness: Adjoint Correspondence U_P† ∘ ι = ι ∘ R_P⁻¹
8. Corollary 1 Witness: Finite-Domain Permutation Matrix Unitarity [U_P]† [U_P] = I and [U_P] [U_P]† = I
9. Corollary 2 Witness: Identity Extension over Complementary Domain C_R \ D
10. Counterexample Witness: Injectivity Collision Rejection
"""

import unittest
import math
from src.module1.utm.model import Direction, UTMProgram, TransitionAction
from src.module2.rutm.model import (
    RUTMConfiguration,
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


class TestStage4UnitaryProofWitnesses(unittest.TestCase):
    """Executable witness test suite for Stage 4 formal proofs."""

    def setUp(self) -> None:
        """Sets up test UTM program, RUTM configurations, and lifted operators."""
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

    def test_01_theorem1_left_unitarity(self) -> None:
        """Witness for Theorem 1: U_P† U_P = I on arbitrary complex state vector."""
        psi = QTMStateVector({self.b0: 0.6 + 0.2j, self.b1: 0.3 - 0.7j})
        u_psi = self.operator.apply_state(psi)
        u_adj_u_psi = self.operator.apply_state_adjoint(u_psi)

        self.assertEqual(u_adj_u_psi, psi)

    def test_02_theorem2_right_unitarity(self) -> None:
        """Witness for Theorem 2: U_P U_P† = I on arbitrary complex state vector."""
        psi = QTMStateVector({self.b1: 1.0 / math.sqrt(2.0), self.b2: 1j / math.sqrt(2.0)})
        u_adj_psi = self.operator.apply_state_adjoint(psi)
        u_u_adj_psi = self.operator.apply_state(u_adj_psi)

        self.assertEqual(u_u_adj_psi, psi)

    def test_03_theorem4_norm_preservation(self) -> None:
        """Witness for Theorem 4: ||U_P ψ|| = ||ψ|| for unnormalized and normalized states."""
        psi_unnorm = QTMStateVector({self.b0: 3.0, self.b1: 4.0j})
        norm_before = psi_unnorm.norm()
        u_psi = self.operator.apply_state(psi_unnorm)
        norm_after = u_psi.norm()

        self.assertAlmostEqual(norm_before, 5.0)
        self.assertAlmostEqual(norm_after, 5.0)
        self.assertAlmostEqual(norm_before, norm_after)

    def test_04_theorem5_inner_product_preservation(self) -> None:
        """Witness for Theorem 5: ⟨U_P ψ | U_P φ⟩ = ⟨ψ | φ⟩."""
        psi = QTMStateVector({self.b0: 1.0 / math.sqrt(2.0), self.b1: 1j / math.sqrt(2.0)})
        phi = QTMStateVector({self.b0: 1j / math.sqrt(2.0), self.b1: 1.0 / math.sqrt(2.0)})

        ip_before = psi.inner_product(phi)
        u_psi = self.operator.apply_state(psi)
        u_phi = self.operator.apply_state(phi)
        ip_after = u_psi.inner_product(u_phi)

        self.assertAlmostEqual(ip_before.real, ip_after.real)
        self.assertAlmostEqual(ip_before.imag, ip_after.imag)

    def test_05_theorem6_basis_orthogonality_preservation(self) -> None:
        """Witness for Theorem 6: ⟨U_P C_1 | U_P C_2⟩ = δ_(C_1, C_2)."""
        u_b0 = self.operator.apply_basis(self.b0)
        u_b1 = self.operator.apply_basis(self.b1)

        # Same basis
        self.assertEqual(basis_inner_product(u_b0, u_b0), 1.0 + 0.0j)
        # Distinct basis
        self.assertEqual(basis_inner_product(u_b0, u_b1), 0.0 + 0.0j)

    def test_06_theorem7_forward_commuting_correspondence(self) -> None:
        """Witness for Theorem 7: U_P ∘ ι = ι ∘ R_P."""
        # Path A: (ι ∘ R_P)(C0)
        c0_next = forward_step_rutm(self.c0, self.program)
        path_a = iota(c0_next)

        # Path B: (U_P ∘ ι)(C0)
        path_b = self.operator.apply_basis(self.b0)

        self.assertEqual(path_a, path_b)

    def test_07_theorem8_adjoint_commuting_correspondence(self) -> None:
        """Witness for Theorem 8: U_P† ∘ ι = ι ∘ R_P⁻¹."""
        # Path A: (ι ∘ R_P⁻¹)(C1)
        c1_prev = reverse_step_rutm(self.c1, self.program)
        path_a = iota(c1_prev)

        # Path B: (U_P† ∘ ι)(C1)
        path_b = self.operator.apply_basis_adjoint(self.b1)

        self.assertEqual(path_a, path_b)

    def test_08_corollary1_finite_matrix_unitarity(self) -> None:
        """Witness for Corollary 1: [U_P]† [U_P] = I_N and [U_P] [U_P]† = I_N."""
        mapping = {self.b0: self.b1, self.b1: self.b2, self.b2: self.b0}
        u_cycle = create_unitary_operator_from_mapping(mapping)

        matrix_rep = u_cycle.get_permutation_matrix([self.b0, self.b1, self.b2])
        self.assertTrue(matrix_rep.is_permutation())
        self.assertTrue(matrix_rep.is_unitary())

    def test_09_corollary2_identity_extension(self) -> None:
        r"""Witness for Corollary 2: Identity extension over C_R \ D maintains global bijectivity."""
        mapping = {self.b0: self.b1, self.b1: self.b0}
        u = create_unitary_operator_from_mapping(mapping)

        # Config outside explicit domain D
        c_ext = create_initial_rutm_configuration({10: "1"}, initial_state="q_ext")
        b_ext = iota(c_ext)

        self.assertEqual(u.apply_basis(b_ext), b_ext)
        self.assertEqual(u.apply_basis_adjoint(b_ext), b_ext)

    def test_10_counterexample_collision_rejection(self) -> None:
        """Witness for Necessity Analysis: Collision mapping fails bijectivity and operator construction."""
        collision_mapping = {self.b0: self.b2, self.b1: self.b2, self.b2: self.b0}
        with self.assertRaises(ValueError):
            create_unitary_operator_from_mapping(collision_mapping)


if __name__ == "__main__":
    unittest.main()
