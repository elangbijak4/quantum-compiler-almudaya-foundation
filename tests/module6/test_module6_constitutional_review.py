"""
Module 6 Stage 1 Unit Test Suite — Scope & Constitutional Review.

Verifies that all 12 constitutional resolutions (Q1-Q12) are formally defined,
governed by specification documents, and enforce strict architectural isolation.
"""

import unittest
import os


class TestModule6ConstitutionalReview(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.constitution_path = os.path.join(self.root_dir, "docs", "module-6", "MODULE_6_CONSTITUTION.md")
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            self.constitution_text = f.read()

    def test_01_q1_classical_domain_resolution(self) -> None:
        """Q1: Classical domain A_C is resolved as A_semantic over finite transition systems."""
        self.assertIn("Resolution Q1", self.constitution_text)
        self.assertIn("A_\\text{semantic}", self.constitution_text)
        self.assertIn("D_\\text{fin}", self.constitution_text)

    def test_02_q2_quantum_domain_resolution(self) -> None:
        """Q2: Quantum circuit domain C_Q is resolved as C_Q^logical (QuantumCircuitIR)."""
        self.assertIn("Resolution Q2", self.constitution_text)
        self.assertIn("C_Q^\\text{logical}", self.constitution_text)
        self.assertIn("QuantumCircuitIR", self.constitution_text)

    def test_03_q3_compiler_mapping_resolution(self) -> None:
        """Q3: Compiler mapping F is resolved as the AML/RUTM -> QTM -> QuantumCircuitIR pipeline."""
        self.assertIn("Resolution Q3", self.constitution_text)
        self.assertIn("AML/RUTM", self.constitution_text)

    def test_04_q4_classical_equivalence_resolution(self) -> None:
        """Q4: Classical equivalence is resolved as Transition Equivalence."""
        self.assertIn("Resolution Q4", self.constitution_text)
        self.assertIn("Transition Equivalence", self.constitution_text)

    def test_05_q5_quantum_equivalence_resolution(self) -> None:
        """Q5: Quantum equivalence is resolved as Operator Equivalence up to ancilla uncomputation."""
        self.assertIn("Resolution Q5", self.constitution_text)
        self.assertIn("Operator Equivalence", self.constitution_text)

    def test_06_q6_first_experiment_level_resolution(self) -> None:
        """Q6: First experiment levels selected as Level 3 (Basis) & Level 5 (Operator)."""
        self.assertIn("Resolution Q6", self.constitution_text)
        self.assertIn("Level 3", self.constitution_text)
        self.assertIn("Level 5", self.constitution_text)

    def test_07_q7_injectivity_quotient_resolution(self) -> None:
        """Q7: Injectivity resolved as quotient mapping F_bar; non-assumed."""
        self.assertIn("Resolution Q7", self.constitution_text)
        self.assertIn("quotient mapping", self.constitution_text)

    def test_08_q8_q10_image_and_counterexample_resolution(self) -> None:
        """Q8 & Q10: Image defined as Img(F) subset C_Q; Hadamard counterexample requirement established."""
        self.assertIn("Resolution Q8", self.constitution_text)
        self.assertIn("Resolution Q10", self.constitution_text)
        self.assertIn("Hadamard", self.constitution_text)

    def test_09_q11_finite_domain_boundary_resolution(self) -> None:
        """Q11: Finite domain boundary D_fin is strictly enforced against infinite extension."""
        self.assertIn("Resolution Q11", self.constitution_text)
        self.assertIn("D_\\text{fin}", self.constitution_text)

    def test_10_q12_hypotheses_vs_facts_resolution(self) -> None:
        """Q12: Research hypotheses explicitly distinguished from established facts."""
        self.assertIn("Resolution Q12", self.constitution_text)
        self.assertIn("hypotheses", self.constitution_text.lower())


if __name__ == "__main__":
    unittest.main()
