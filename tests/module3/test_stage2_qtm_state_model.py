"""
Module 3 Stage 2 Test Suite — QTM State Model & Hilbert Space Representation.

Verifies:
1. Computational basis state construction & configuration semantic identity
2. Configuration embedding ι(C_R) = |C_R⟩
3. Basis state orthogonality ⟨C_1|C_2⟩ = δ(C_1, C_2)
4. Complex amplitudes α_C ∈ ℂ and sparse superposition representations
5. Quantum state vector arithmetic (+, -, scalar multiplication)
6. Complex inner product ⟨ψ|φ⟩ with correct Hermitian conjugation
7. Vector norm calculation ||ψ|| = sqrt(⟨ψ|ψ⟩)
8. Normalized quantum state verification (is_normalized)
9. Zero vector handling (|0⟩_vec norm = 0, non-normalizable)
10. Immutability and non-aliasing properties
11. Numerical sparsification semantics vs mathematical zero distinction
"""

import unittest
import math
from src.module1.utm.model import Direction
from src.module2.rutm.model import (
    RUTMConfiguration,
    HistoryRecord,
    create_initial_rutm_configuration,
)
from src.module3.qtm.basis import (
    QuantumBasisState,
    iota,
    basis_inner_product,
)
from src.module3.qtm.state import (
    QTMStateVector,
    DEFAULT_TOLERANCE,
    basis_state_vector,
    zero_state_vector,
)


class TestStage2QTMStateModel(unittest.TestCase):
    """Unit test suite for Module 3 Stage 2 executable state space model."""

    def setUp(self) -> None:
        """Sets up test configurations."""
        self.config_0 = create_initial_rutm_configuration(
            tape={0: "1", 1: "0"}, initial_state="q_start"
        )
        self.config_1 = RUTMConfiguration(
            current_state="q_step1",
            tape={0: "1", 1: "1"},
            head_pos=1,
            history=(HistoryRecord("q_start", "0", Direction.RIGHT),),
            step_count=1,
            halted=False,
            error=None,
        )
        self.config_2 = RUTMConfiguration(
            current_state="q_halt",
            tape={0: "1", 1: "1"},
            head_pos=1,
            history=(
                HistoryRecord("q_start", "0", Direction.RIGHT),
                HistoryRecord("q_step1", "1", Direction.STAY),
            ),
            step_count=2,
            halted=True,
            error=None,
        )

    def test_01_basis_state_construction_and_identity(self) -> None:
        """Test basis state construction and semantic configuration identity."""
        b0 = iota(self.config_0)
        self.assertIsInstance(b0, QuantumBasisState)
        self.assertEqual(b0.config.current_state, "q_start")

        # Duplicate config object with identical values
        config_0_dup = create_initial_rutm_configuration(
            tape={0: "1", 1: "0"}, initial_state="q_start"
        )
        b0_dup = QuantumBasisState(config_0_dup)

        self.assertEqual(b0, b0_dup)
        self.assertEqual(hash(b0), hash(b0_dup))

        # Different config
        b1 = QuantumBasisState(self.config_1)
        self.assertNotEqual(b0, b1)

    def test_02_basis_orthogonality(self) -> None:
        """Test Dirac inner product basis orthogonality ⟨C_1|C_2⟩ = δ(C_1, C_2)."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        self.assertEqual(basis_inner_product(b0, b0), 1.0 + 0.0j)
        self.assertEqual(basis_inner_product(b1, b1), 1.0 + 0.0j)
        self.assertEqual(basis_inner_product(b0, b1), 0.0 + 0.0j)
        self.assertEqual(basis_inner_product(b1, b0), 0.0 + 0.0j)

    def test_03_basis_state_vector(self) -> None:
        """Test single basis state vector construction and norm."""
        v0 = basis_state_vector(self.config_0)
        self.assertEqual(v0.dimension, 1)
        self.assertAlmostEqual(v0.norm(), 1.0)
        self.assertTrue(v0.is_normalized())
        self.assertFalse(v0.is_zero())

    def test_04_complex_amplitudes_and_superposition(self) -> None:
        """Test sparse state vectors with complex amplitudes α_C ∈ ℂ."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        amp0 = 1.0 / math.sqrt(2.0)
        amp1 = 1j / math.sqrt(2.0)

        psi = QTMStateVector({b0: amp0, b1: amp1})
        self.assertEqual(psi.dimension, 2)
        self.assertAlmostEqual(psi.get_amplitude(b0), amp0)
        self.assertAlmostEqual(psi.get_amplitude(b1), amp1)
        self.assertAlmostEqual(psi.norm(), 1.0)
        self.assertTrue(psi.is_normalized())

    def test_05_state_addition_and_subtraction(self) -> None:
        """Test vector addition |ψ⟩ + |φ⟩ and subtraction |ψ⟩ - |φ⟩."""
        v0 = basis_state_vector(self.config_0)
        v1 = basis_state_vector(self.config_1)

        v_sum = v0 + v1
        self.assertEqual(v_sum.dimension, 2)
        self.assertAlmostEqual(v_sum.norm(), math.sqrt(2.0))
        self.assertFalse(v_sum.is_normalized())

        v_diff = v_sum - v1
        self.assertEqual(v_diff, v0)

    def test_06_scalar_multiplication(self) -> None:
        """Test scalar multiplication c |ψ⟩ with real and complex scalars."""
        b0 = iota(self.config_0)
        v0 = basis_state_vector(self.config_0)

        v_scaled = (1.0 / math.sqrt(2.0)) * v0
        self.assertAlmostEqual(v_scaled.get_amplitude(b0), 1.0 / math.sqrt(2.0))
        self.assertAlmostEqual(v_scaled.norm(), 1.0 / math.sqrt(2.0))

        v_complex = (2j) * v0
        self.assertAlmostEqual(v_complex.get_amplitude(b0), 2j)
        self.assertAlmostEqual(v_complex.norm(), 2.0)

    def test_07_complex_inner_product(self) -> None:
        """Test inner product ⟨ψ|φ⟩ = Σ α_C* β_C with complex conjugation."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        psi = QTMStateVector({b0: 1j / math.sqrt(2), b1: 1.0 / math.sqrt(2)})
        phi = QTMStateVector({b0: 1.0 / math.sqrt(2), b1: 1j / math.sqrt(2)})

        # ⟨psi|phi⟩ = (1j)* (1/√2) + (1/√2)* (1j/√2) = (-1j)(1/2) + (1/2)(1j) = -0.5j + 0.5j = 0.0
        ip = psi.inner_product(phi)
        self.assertAlmostEqual(ip.real, 0.0)
        self.assertAlmostEqual(ip.imag, 0.0)

        # ⟨psi|psi⟩ = |1j/√2|² + |1/√2|² = 0.5 + 0.5 = 1.0
        self.assertAlmostEqual(psi.inner_product(psi).real, 1.0)
        self.assertAlmostEqual(psi.inner_product(psi).imag, 0.0)

    def test_08_norm_and_normalization(self) -> None:
        """Test norm calculation and normalize() operation."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        unnormalized = QTMStateVector({b0: 3.0, b1: 4.0})
        self.assertAlmostEqual(unnormalized.norm(), 5.0)
        self.assertFalse(unnormalized.is_normalized())

        normalized = unnormalized.normalize()
        self.assertAlmostEqual(normalized.norm(), 1.0)
        self.assertTrue(normalized.is_normalized())
        self.assertAlmostEqual(normalized.get_amplitude(b0), 0.6)
        self.assertAlmostEqual(normalized.get_amplitude(b1), 0.8)

    def test_09_zero_vector_handling(self) -> None:
        """Test zero vector |0⟩_vec behaviors."""
        z = zero_state_vector()
        self.assertEqual(z.dimension, 0)
        self.assertEqual(z.norm(), 0.0)
        self.assertTrue(z.is_zero())
        self.assertFalse(z.is_normalized())

        with self.assertRaises(ValueError):
            z.normalize()

    def test_10_immutability_and_non_aliasing(self) -> None:
        """Test that operations do not modify operand state vectors."""
        v0 = basis_state_vector(self.config_0)
        v1 = basis_state_vector(self.config_1)

        orig_v0_norm = v0.norm()
        orig_v1_norm = v1.norm()

        _ = v0 + v1
        _ = v0 * 3.5

        self.assertEqual(v0.norm(), orig_v0_norm)
        self.assertEqual(v1.norm(), orig_v1_norm)
        self.assertEqual(v0.dimension, 1)

    def test_11_invalid_inputs(self) -> None:
        """Test rejection of invalid basis states and non-numeric amplitudes."""
        with self.assertRaises(TypeError):
            QuantumBasisState("not_a_config")  # type: ignore

        with self.assertRaises(TypeError):
            QTMStateVector({"invalid_key": 1.0})  # type: ignore

        b0 = iota(self.config_0)
        with self.assertRaises(TypeError):
            QTMStateVector({b0: "non_numeric"})  # type: ignore

    def test_12_exact_zero_amplitude_omitted(self) -> None:
        """Test A: An amplitude exactly equal to 0.0 + 0.0j is omitted from sparse map."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        v = QTMStateVector({b0: 1.0, b1: 0.0 + 0.0j})
        self.assertEqual(v.dimension, 1)
        self.assertIn(b0, v.amplitudes)
        self.assertNotIn(b1, v.amplitudes)
        self.assertEqual(v.get_amplitude(b1), 0.0 + 0.0j)

    def test_13_below_threshold_amplitude_omitted(self) -> None:
        """Test B: Amplitude magnitude below configured threshold is omitted by sparsification policy."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        # 1e-15 < DEFAULT_TOLERANCE (1e-12)
        v = QTMStateVector({b0: 1.0, b1: 1e-15}, tol=DEFAULT_TOLERANCE)
        self.assertEqual(v.dimension, 1)
        self.assertNotIn(b1, v.amplitudes)

    def test_14_non_negligible_amplitude_retained(self) -> None:
        """Test C: Non-negligible amplitude above threshold is retained."""
        b0 = iota(self.config_0)
        b1 = iota(self.config_1)

        # 1e-10 > DEFAULT_TOLERANCE (1e-12)
        v = QTMStateVector({b0: 1.0, b1: 1e-10}, tol=DEFAULT_TOLERANCE)
        self.assertEqual(v.dimension, 2)
        self.assertIn(b1, v.amplitudes)
        self.assertEqual(v.get_amplitude(b1), 1e-10)

    def test_15_basis_identity_independent_of_tolerance(self) -> None:
        """Test D: Basis configuration identity is exact and independent of numerical tolerance."""
        b0 = iota(self.config_0)
        b0_dup = QuantumBasisState(
            create_initial_rutm_configuration(tape={0: "1", 1: "0"}, initial_state="q_start")
        )
        b1 = iota(self.config_1)

        self.assertEqual(b0, b0_dup)
        self.assertNotEqual(b0, b1)
        self.assertEqual(basis_inner_product(b0, b0_dup), 1.0 + 0.0j)
        self.assertEqual(basis_inner_product(b0, b1), 0.0 + 0.0j)

    def test_16_normalization_verification_predicate(self) -> None:
        """Test E: is_normalized() is an executable numerical predicate with configurable tolerance."""
        b0 = iota(self.config_0)

        v_exact = QTMStateVector({b0: 1.0})
        self.assertTrue(v_exact.is_normalized(tol=1e-12))

        v_approx = QTMStateVector({b0: 1.00000000001})
        self.assertTrue(v_approx.is_normalized(tol=1e-10))
        self.assertFalse(v_approx.is_normalized(tol=1e-15))


if __name__ == "__main__":
    unittest.main()
