"""
Module 6 Stage 5 Unit Test Suite — Backward Compatibility Invariant.

Verifies Img_N(F_G0) \subseteq Img_N(F_G') backward compatibility invariant.
"""

import unittest
from src.module6.evolution import ExtendedVocabularyEvaluator


class TestStage5BackwardCompatibility(unittest.TestCase):
    def test_01_backward_compatibility_preserved(self) -> None:
        """Positive test: Extended image superset of baseline image passes."""
        g0_img = {"PERM_1", "PERM_2"}
        g_ext_img = {"PERM_1", "PERM_2", "SUPERPOS_1"}

        is_compat = ExtendedVocabularyEvaluator.evaluate_backward_compatibility(g0_img, g_ext_img)
        self.assertTrue(is_compat)

    def test_02_backward_compatibility_violated(self) -> None:
        """Negative test: Extended image missing baseline element fails backward compatibility."""
        g0_img = {"PERM_1", "PERM_2"}
        g_ext_img = {"PERM_1", "SUPERPOS_1"}  # PERM_2 missing

        is_compat = ExtendedVocabularyEvaluator.evaluate_backward_compatibility(g0_img, g_ext_img)
        self.assertFalse(is_compat)


if __name__ == "__main__":
    unittest.main()
