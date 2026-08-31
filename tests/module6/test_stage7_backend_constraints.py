"""
Module 6 Stage 7 Test Suite — Backend Restrictions.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7BackendConstraints(unittest.TestCase):
    """Tests for backend constraint restrictions G_effective = Bu cap G_backend subseteq GE(k)."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_backend_restricts_effective_vocabulary(self) -> None:
        """Req 12: Backend constraints restrict permitted gates, never expand them."""
        backend_c = {"supported_gates": ["CNOT", "X"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, backend_constraints=backend_c
        )
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "X"))

    def test_backend_cannot_expand_vocabulary(self) -> None:
        """Req 12: Backend claiming support for gate outside GE(0) cannot expand effective vocabulary."""
        backend_c = {"supported_gates": ["CNOT", "X", "HADAMARD", "RIGETTI_CZ"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, backend_constraints=backend_c
        )
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "X"))


if __name__ == "__main__":
    unittest.main()
