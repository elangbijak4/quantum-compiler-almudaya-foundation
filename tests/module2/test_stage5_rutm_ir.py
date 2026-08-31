"""
Unit Tests for Module 2 Stage 5: RUTM-IR Model (Closure Patched).

Strictly compliant with Stage 5 requirements (main-technical-refference.md & STAGE_5_RUTM_IR.md).
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module2.rutm_ir.model import (
    RUTM_IR,
    RUTMHistoryPolicy,
    RUTMProvenance,
    create_initial_configuration_from_ir,
)
from src.module2.rutm_ir.validator import validate_rutm_ir
from src.module2.rutm_ir.serialization import serialize_rutm_ir, deserialize_rutm_ir


class TestStage5RUTMIR(unittest.TestCase):
    """Stage 5 RUTM-IR Model & Serialization Test Suite."""

    def setUp(self):
        """Construct a standard valid RUTM_IR test object."""
        self.valid_ir = RUTM_IR(
            name="TestMachine_1",
            states=frozenset({"q_start", "q1", "q_halt"}),
            input_alphabet=frozenset({"0", "1"}),
            tape_alphabet=frozenset({"0", "1", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                ("q1", "0"): TransitionAction("q_halt", "0", Direction.STAY),
            },
            history_policy=RUTMHistoryPolicy(enabled=True),
            provenance=RUTMProvenance(
                source_model="RUTM",
                source_stage="Stage 4",
                proof_reference="docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md",
            ),
        )

    def test_1_valid_rutm_ir_construction(self):
        """Test 1: Valid RUTM-IR object construction passes validation."""
        is_valid, err = validate_rutm_ir(self.valid_ir)
        self.assertTrue(is_valid, f"Validation failed: {err}")
        self.assertIsNone(err)

    def test_2_invalid_empty_states(self):
        """Test 2: Rejection of empty states set."""
        ir = RUTM_IR(
            name="EmptyStates",
            states=frozenset(),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("States set cannot be empty", err)

    def test_3_invalid_blank_symbol(self):
        """Test 3: Rejection of blank symbol outside tape alphabet."""
        ir = RUTM_IR(
            name="BadBlank",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0"}),  # '_' missing
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Blank symbol", err)

    def test_4_invalid_initial_state(self):
        """Test 4: Rejection of initial state not in states set."""
        ir = RUTM_IR(
            name="BadInitial",
            states=frozenset({"q1", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_nonexistent",
            halt_state="q_halt",
            transitions={},
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Initial state", err)

    def test_5_invalid_halt_state(self):
        """Test 5: Rejection of halt state not in states set."""
        ir = RUTM_IR(
            name="BadHalt",
            states=frozenset({"q_start", "q1"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt_nonexistent",
            transitions={},
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Halt state", err)

    def test_6_invalid_transition_source(self):
        """Test 6: Rejection of transition source state not in states set."""
        ir = RUTM_IR(
            name="BadTransSource",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_unknown", "0"): TransitionAction("q_halt", "0", Direction.RIGHT)
            },
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Transition source state", err)

    def test_7_invalid_transition_symbol(self):
        """Test 7: Rejection of transition read symbol not in tape alphabet."""
        ir = RUTM_IR(
            name="BadTransSym",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "9"): TransitionAction("q_halt", "0", Direction.RIGHT)
            },
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Transition read symbol", err)

    def test_8_invalid_target_state(self):
        """Test 8: Rejection of transition target state not in states set."""
        ir = RUTM_IR(
            name="BadTargetState",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q_unknown", "0", Direction.RIGHT)
            },
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Transition action target state", err)

    def test_9_invalid_write_symbol(self):
        """Test 9: Rejection of transition write symbol not in tape alphabet."""
        ir = RUTM_IR(
            name="BadWriteSym",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q_halt", "9", Direction.RIGHT)
            },
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Transition action write symbol", err)

    def test_10_invalid_direction(self):
        """Test 10: Rejection of invalid direction (non-Direction enum)."""
        ir = RUTM_IR(
            name="BadDirection",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q_halt", "0", "UP")  # Invalid
            },
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Direction enum", err)

    def test_11_halt_state_transition_rejection(self):
        """Test 11: Rejection of transitions originating from halt_state. Note: Python dictionary structure inherently prevents duplicate key conflicts."""
        ir = RUTM_IR(
            name="HaltTrans",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_halt", "0"): TransitionAction("q_start", "0", Direction.RIGHT)
            },
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("out of halt_state", err)

    def test_12_deterministic_transition_acceptance(self):
        """Test 12: Unique deterministic transitions dictionary is accepted."""
        is_valid, err = validate_rutm_ir(self.valid_ir)
        self.assertTrue(is_valid)

    def test_13_reversible_metadata_validation(self):
        """Test 13: History policy metadata is present and valid."""
        self.assertTrue(self.valid_ir.history_policy.enabled)
        self.assertEqual(
            self.valid_ir.history_policy.record_schema,
            ("prev_state", "overwritten_symbol", "direction"),
        )

    def test_14_provenance_preservation(self):
        """Test 14: Proof provenance metadata is preserved."""
        self.assertEqual(self.valid_ir.provenance.source_model, "RUTM")
        self.assertEqual(self.valid_ir.provenance.source_stage, "Stage 4")
        self.assertEqual(
            self.valid_ir.provenance.proof_reference,
            "docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md",
        )

    def test_15_ir_to_initial_rutm_configuration(self):
        """Test 15: create_initial_configuration_from_ir constructs valid RUTMConfiguration."""
        c0 = create_initial_configuration_from_ir(self.valid_ir, tape={0: "0"})
        self.assertEqual(c0.current_state, "q_start")
        self.assertEqual(c0.head_pos, 0)
        self.assertEqual(c0.step_count, 0)
        self.assertEqual(len(c0.history), 0)
        self.assertFalse(c0.halted)

    def test_16_serialization_round_trip(self):
        """Test 16: Serializing to JSON and deserializing recovers exact RUTM_IR object."""
        json_str = serialize_rutm_ir(self.valid_ir)
        ir_reconstructed = deserialize_rutm_ir(json_str)

        self.assertEqual(ir_reconstructed, self.valid_ir)

    def test_17_canonical_deterministic_serialization(self):
        """Test 17: Identical RUTM_IR objects with different set construction order serialize to identical strings."""
        ir1 = RUTM_IR(
            name="MachineA",
            states=frozenset({"q2", "q1", "q_start", "q_halt"}),
            input_alphabet=frozenset({"1", "0"}),
            tape_alphabet=frozenset({"_", "1", "0"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        ir2 = RUTM_IR(
            name="MachineA",
            states=frozenset({"q_start", "q_halt", "q1", "q2"}),
            input_alphabet=frozenset({"0", "1"}),
            tape_alphabet=frozenset({"0", "_", "1"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )

        s1 = serialize_rutm_ir(ir1)
        s2 = serialize_rutm_ir(ir2)
        self.assertEqual(s1, s2)

    def test_18_differential_semantic_equivalence(self):
        """Test 18: Operational step using IR-derived UTMProgram matches expected Stage 3 behavior."""
        program = self.valid_ir.to_utm_program()
        c0 = create_initial_configuration_from_ir(self.valid_ir, tape={0: "0"})

        c1 = forward_step_rutm(c0, program)
        self.assertEqual(c1.current_state, "q1")
        self.assertEqual(c1.tape[0], "1")
        self.assertEqual(c1.head_pos, 1)
        self.assertEqual(c1.step_count, 1)

        c0_restored = reverse_step_rutm(c1, program=program)
        self.assertEqual(c0_restored, c0)

    # -------------------------------------------------------------------------
    # Closure Patch #1 Tests (History Policy Validation)
    # -------------------------------------------------------------------------

    def test_19_invalid_history_schema_rejected(self):
        """Test 19 (Closure Patch Item #1): Rejection of unsupported history record_schema."""
        bad_policy = RUTMHistoryPolicy(
            enabled=True,
            record_schema=("state", "symbol"),  # Unsupported schema
        )
        ir = RUTM_IR(
            name="BadSchema",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
            history_policy=bad_policy,
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported history policy record_schema", err)

    def test_20_invalid_inverse_policy_rejected(self):
        """Test 20 (Closure Patch Item #1): Rejection of unsupported inverse_policy."""
        bad_policy = RUTMHistoryPolicy(
            enabled=True,
            inverse_policy="FIFO_queue",  # Unsupported policy
        )
        ir = RUTM_IR(
            name="BadInversePolicy",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
            history_policy=bad_policy,
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported history policy inverse_policy", err)

    # -------------------------------------------------------------------------
    # Micro Closure Patch Tests (source_stage Provenance Validation)
    # -------------------------------------------------------------------------

    def test_21_invalid_provenance_source_stage_rejected(self):
        """Test 21 (Micro Closure Patch): Rejection of empty or invalid provenance source_stage."""
        bad_prov = RUTMProvenance(
            source_model="RUTM",
            source_stage="",  # Empty string
            proof_reference="docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md",
        )
        ir = RUTM_IR(
            name="BadSourceStage",
            states=frozenset({"q_start", "q_halt"}),
            input_alphabet=frozenset({"0"}),
            tape_alphabet=frozenset({"0", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
            provenance=bad_prov,
        )
        is_valid, err = validate_rutm_ir(ir)
        self.assertFalse(is_valid)
        self.assertIn("source_stage", err)


if __name__ == "__main__":
    unittest.main()
