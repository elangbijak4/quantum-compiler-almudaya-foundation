"""
Module 6 Stage 7 Test Suite — Provenance Integrity.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7Provenance(unittest.TestCase):
    """Tests for complete resolution context provenance metadata."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_provenance_contains_mandatory_keys(self) -> None:
        """Req 30: Provenance records evolution stage, session ID, baseline mode, and effective vocabulary."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.assertIn("evolution_stage", ctx.provenance)
        self.assertIn("session_id", ctx.provenance)
        self.assertIn("baseline_mode", ctx.provenance)
        self.assertIn("effective_vocabulary", ctx.provenance)
        self.assertIn("resolution_provenance_id", ctx.provenance)


if __name__ == "__main__":
    unittest.main()
