"""
Module 6 Micro-Closure Governance Test Suite.

Verifies frozen micro-closure specifications, definitions, and invariant boundaries.
"""

import unittest
import os


class TestModule6MicroClosure(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.mc_path = os.path.join(self.root_dir, "docs", "module-6", "MODULE_6_MICRO_CLOSURE.md")

        with open(self.mc_path, "r", encoding="utf-8") as f:
            self.mc_text = f.read()

    def test_01_micro_closure_file_exists(self) -> None:
        """Test 01: Verify MODULE_6_MICRO_CLOSURE.md exists and is non-empty."""
        self.assertTrue(os.path.exists(self.mc_path))
        self.assertGreater(len(self.mc_text), 100)

    def test_02_micro_closure_status(self) -> None:
        """Test 02: Verify micro-closure document contains frozen status."""
        self.assertIn("FORMALLY CLOSED / FROZEN", self.mc_text)

    def test_03_absolute_upstream_boundary(self) -> None:
        """Test 03: Verify upstream Modules 1-5 boundary is declared frozen."""
        self.assertTrue("Modules 1" in self.mc_text and "FORMALLY COMPLETE / FROZEN" in self.mc_text)

    def test_04_classical_domain_definition(self) -> None:
        """Test 04: Verify classical algorithm domain definition A_C = A_semantic."""
        self.assertTrue(r"A_\text{semantic}" in self.mc_text or "A_semantic" in self.mc_text)

    def test_05_compiler_mapping_definition(self) -> None:
        """Test 05: Verify compiler mapping definition F: A_C -> C_Q^logical."""
        self.assertTrue("F :" in self.mc_text or "F:" in self.mc_text)

    def test_06_image_definition(self) -> None:
        """Test 06: Verify compiler image definition Img(F)."""
        self.assertTrue(r"\text{Img}(F)" in self.mc_text or "Img(F)" in self.mc_text)

    def test_07_quantum_semantic_equivalence(self) -> None:
        """Test 07: Verify quantum semantic equivalence definition \equiv_Q."""
        self.assertTrue(r"\equiv_Q" in self.mc_text or "=_Q" in self.mc_text)

    def test_08_classical_semantic_equivalence(self) -> None:
        """Test 08: Verify classical semantic equivalence definition \equiv_C."""
        self.assertTrue(r"\equiv_C" in self.mc_text or "=_C" in self.mc_text)

    def test_09_quotient_mapping_definition(self) -> None:
        """Test 09: Verify quotient mapping F_bar definition."""
        self.assertTrue("F_bar" in self.mc_text or r"\bar{F}" in self.mc_text)

    def test_10_injectivity_unproven_property(self) -> None:
        """Test 10: Injectivity remains an unproven research property."""
        self.assertIn("Injectivity: UNPROVEN", self.mc_text)

    def test_11_surjectivity_unproven_property(self) -> None:
        """Test 11: Surjectivity remains an unproven research property."""
        self.assertIn("Surjectivity: UNPROVEN", self.mc_text)

    def test_12_hadamard_counterexample_hypothesis(self) -> None:
        """Test 12: Hadamard non-surjectivity remains an open hypothesis."""
        self.assertIn("OPEN HYPOTHESIS", self.mc_text)

    def test_13_authorized_expressibility_subpackage(self) -> None:
        """Test 13: Verify src/module6/expressibility contains authorized Stage 2 expressibility modules."""
        d = os.path.join(self.root_dir, "src", "module6", "expressibility")
        files = set(f for f in os.listdir(d) if not f.endswith(".pyc") and f != "__pycache__")
        expected = {"__init__.py", "config.py", "matcher.py", "report.py"}
        self.assertEqual(files, expected, f"Expressibility files in {d}: {files}")

    def test_14_upstream_modules_untouched(self) -> None:
        """Test 14: Verify src/module1 through src/module5 exist and are accessible."""
        for mod_num in range(1, 6):
            d = os.path.join(self.root_dir, "src", f"module{mod_num}")
            self.assertTrue(os.path.isdir(d), f"Upstream directory missing: {d}")


if __name__ == "__main__":
    unittest.main()
