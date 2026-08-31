"""
Module 6 Stage 7 Test Suite — Initialization & Constitutional Verification.
"""

import unittest

from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.resolution import (
    Stage7CompilerResolver,
    ConfigurationStatus,
    ConfigurationPrecedence,
    ResolutionPolicy,
    serialize_compilation_context,
    deserialize_compilation_context,
)


class TestStage7Initialization(unittest.TestCase):
    """Tests for Stage 7 Resolution Scaffold stubs and constitutional invariants."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_01_default_resolution_preserves_ge0(self) -> None:
        """Req 6: Default resolution preserves GE(0) evolutionary vocabulary."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.assertEqual(ctx.baseline_mode, BaselineMode.DEFAULT_EVOLUTIONARY.value)
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "TOFFOLI", "X"))
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.VALID_CONFIGURATION)

    def test_02_user_selected_resolution_subset(self) -> None:
        """Req 7: Explicit user baseline subset resolves correctly."""
        sb = SessionBaseline(
            session_id="s_user",
            selected_gates=("CNOT", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb)
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "X"))
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.VALID_CONFIGURATION)

    def test_03_invalid_baseline_outside_ge0_rejected(self) -> None:
        """Req 18: Unavailable gate outside GE(0) marks configuration INVALID."""
        sb_invalid = SessionBaseline(
            session_id="s_bad",
            selected_gates=("HADAMARD", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb_invalid)
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.INVALID_CONFIGURATION)
        self.assertEqual(ctx.effective_vocabulary, ())

    def test_04_precedence_order(self) -> None:
        """Req 16: Deterministic configuration precedence order."""
        order = ResolutionPolicy.get_precedence_order()
        self.assertEqual(len(order), 6)
        self.assertEqual(order[0], ConfigurationPrecedence.EVOLUTIONARY_DEFAULT)

    def test_05_context_serialization_roundtrip(self) -> None:
        """Req 20, 24: Canonical JSON round-trip serialization."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        ctx_json = serialize_compilation_context(ctx)
        des_ctx = deserialize_compilation_context(ctx_json)

        self.assertEqual(des_ctx.evolution_stage, ctx.evolution_stage)
        self.assertEqual(des_ctx.effective_vocabulary, ctx.effective_vocabulary)
        self.assertEqual(des_ctx.configuration_status, ctx.configuration_status)


if __name__ == "__main__":
    unittest.main()
