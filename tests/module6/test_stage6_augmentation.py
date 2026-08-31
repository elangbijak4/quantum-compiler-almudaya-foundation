"""
Module 6 Stage 6 Test Suite — Minimal Gate Augmentation.
"""

import unittest

from src.module6.feasibility.augmentation import MinimalAugmentationAnalyzer


class TestStage6Augmentation(unittest.TestCase):
    """Tests for MinimalAugmentationAnalyzer."""

    def test_find_minimal_augmentation(self) -> None:
        """Req 21: Find C_min = {"HADAMARD"} when superposition missing."""
        bu_gates = ("CNOT", "X")
        ge_gates = ("CNOT", "HADAMARD", "TOFFOLI", "X")
        missing_caps = ("SUPERPOSITION",)

        c_min = MinimalAugmentationAnalyzer.find_minimal_augmentation(bu_gates, ge_gates, missing_caps)
        self.assertEqual(c_min, ("HADAMARD",))

    def test_no_augmentation_when_empty_missing(self) -> None:
        """Req 21: Returns empty tuple when missing capabilities are empty."""
        bu_gates = ("CNOT", "X")
        ge_gates = ("CNOT", "TOFFOLI", "X")

        c_min = MinimalAugmentationAnalyzer.find_minimal_augmentation(bu_gates, ge_gates, ())
        self.assertEqual(c_min, ())


if __name__ == "__main__":
    unittest.main()
