"""
Stage 3 Unit Tests: AML v0.1 Operational Semantics S = (PC, R, M, F).

Strictly verifies Stage 3 compliance per main-technical-refference.md.
"""

import unittest
from src.module1.aml.semantics import (
    Flags,
    AMLState,
    step_operational_semantics,
)


class TestStage3AMLOperationalSemantics(unittest.TestCase):
    """Test suite for Stage 3 AML v0.1 operational semantics state transitions."""

    def setUp(self):
        self.initial_state = AMLState()

    def test_initial_state(self):
        """Verify initial state values S0 = (0, R_0, M_0, F_0)."""
        self.assertEqual(self.initial_state.pc, 0)
        self.assertEqual(len(self.initial_state.registers), 16)
        for r in range(16):
            self.assertEqual(self.initial_state.registers[f"R{r}"], 0)
        self.assertEqual(len(self.initial_state.memory), 0)
        self.assertFalse(self.initial_state.flags.zero)
        self.assertFalse(self.initial_state.flags.halted)
        self.assertIsNone(self.initial_state.flags.error)

    def test_load_and_store_transitions(self):
        """Test LOAD and STORE operational transitions."""
        # Set memory A = 5
        s0 = self.initial_state.copy()
        s0.memory["A"] = 5

        # LOAD R1, A
        s1 = step_operational_semantics(s0, "LOAD", ["R1", "A"])
        self.assertEqual(s1.registers["R1"], 5)
        self.assertEqual(s1.pc, 1)

        # STORE OUT, R1
        s2 = step_operational_semantics(s1, "STORE", ["OUT", "R1"])
        self.assertEqual(s2.memory["OUT"], 5)
        self.assertEqual(s2.pc, 2)

    def test_arithmetic_transitions(self):
        """Test ADD, SUB, MUL operational transitions."""
        s0 = self.initial_state.copy()
        s0.registers["R1"] = 10
        s0.registers["R2"] = 3

        # ADD R1, R2 -> 13
        s1 = step_operational_semantics(s0, "ADD", ["R1", "R2"])
        self.assertEqual(s1.registers["R1"], 13)

        # SUB R1, 5 -> 8
        s2 = step_operational_semantics(s1, "SUB", ["R1", "5"])
        self.assertEqual(s2.registers["R1"], 8)

        # MUL R1, R2 -> 24
        s3 = step_operational_semantics(s2, "MUL", ["R1", "R2"])
        self.assertEqual(s3.registers["R1"], 24)

    def test_cmp_and_conditional_jumps(self):
        """Test CMP flag mutations and JZ / JNZ transitions."""
        s0 = self.initial_state.copy()
        s0.registers["R1"] = 5

        # CMP R1, 5 -> zero flag True (PC becomes 1)
        s1 = step_operational_semantics(s0, "CMP", ["R1", "5"])
        self.assertTrue(s1.flags.zero)

        # JZ 10 -> PC becomes 10 because zero flag is True
        s2 = step_operational_semantics(s1, "JZ", ["10"])
        self.assertEqual(s2.pc, 10)

        # CMP R1, 99 -> zero flag False (PC becomes 11)
        s3 = step_operational_semantics(s2, "CMP", ["R1", "99"])
        self.assertFalse(s3.flags.zero)
        self.assertEqual(s3.pc, 11)

        # JZ 20 -> PC becomes 12 (PC+1) because zero flag is False
        s4 = step_operational_semantics(s3, "JZ", ["20"])
        self.assertEqual(s4.pc, 12)

        # JNZ 50 -> PC becomes 50 because zero flag is False
        s5 = step_operational_semantics(s4, "JNZ", ["50"])
        self.assertEqual(s5.pc, 50)

    def test_halt_transition(self):
        """Test HALT operational transition."""
        s0 = self.initial_state.copy()
        s1 = step_operational_semantics(s0, "HALT", [])
        self.assertTrue(s1.flags.halted)

    def test_poc_trace_simulation(self):
        """
        Simulate the exact operational state transitions for the first PoC program:
        A = 5, B = 7 => OUT = 12
        """
        s = AMLState()
        s.memory["A"] = 5
        s.memory["B"] = 7

        # 1. LOAD R1, A
        s = step_operational_semantics(s, "LOAD", ["R1", "A"])
        self.assertEqual(s.registers["R1"], 5)
        self.assertEqual(s.pc, 1)

        # 2. LOAD R2, B
        s = step_operational_semantics(s, "LOAD", ["R2", "B"])
        self.assertEqual(s.registers["R2"], 7)
        self.assertEqual(s.pc, 2)

        # 3. ADD R1, R2
        s = step_operational_semantics(s, "ADD", ["R1", "R2"])
        self.assertEqual(s.registers["R1"], 12)
        self.assertEqual(s.pc, 3)

        # 4. STORE OUT, R1
        s = step_operational_semantics(s, "STORE", ["OUT", "R1"])
        self.assertEqual(s.memory["OUT"], 12)
        self.assertEqual(s.pc, 4)

        # 5. HALT
        s = step_operational_semantics(s, "HALT", [])
        self.assertTrue(s.flags.halted)
        self.assertEqual(s.memory["OUT"], 12)


if __name__ == "__main__":
    unittest.main()
