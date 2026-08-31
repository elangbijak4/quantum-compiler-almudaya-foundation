"""
Module 3 Stage 9 Test Suite — Completion Gate & Self-Auditing Integration Gate.

Verifies:
1. test_stage_audit
2. test_full_module3_regression
3. test_end_to_end_pipeline
4. test_mathematical_invariant_audit
5. test_qtm_ir_validation_audit
6. test_translator_audit
7. test_execution_audit
8. test_equivalence_audit
9. test_negative_wrong_transition_detected
10. test_negative_wrong_basis_detected
11. test_negative_extra_amplitude_detected
12. test_negative_domain_truncation_detected
13. test_history_integrity_audit
14. test_halting_integrity_audit
15. test_error_integrity_audit
16. test_serialization_integrity_audit
17. test_determinism_audit
18. test_provenance_audit
19. test_public_api_audit
20. test_module4_boundary_audit
"""

import unittest
import os

from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import (
    HistoryRecord,
    RUTMConfiguration,
    create_initial_rutm_configuration,
)
from src.module3.completion import (
    Module3CompletionStatus,
    Module3CompletionGate,
    run_module3_completion_gate,
)
from src.module3.qtm import iota
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRComplexNumber,
    CANONICAL_SEMANTIC_RELATION,
)
from src.module3.qtm_ir.validator import validate_qtm_ir
from src.module3.qtm_ir.serialization import (
    serialize_qtm_ir_to_json,
    deserialize_qtm_ir_from_json,
)
from src.module3.translator import (
    translate_rutm_to_qtm_ir,
    compute_canonical_basis_id,
)
from src.module3.execution import apply_unitary, execute
from src.module3.equivalence import verify_equivalence, EquivalenceStatus


class TestStage9CompletionGate(unittest.TestCase):
    """Unit test suite for Stage 9 Completion Gate."""

    def setUp(self) -> None:
        """Sets up completion gate fixture."""
        self.gate = Module3CompletionGate(repo_root="d:/quantum-compiler")
        self.utm_program = UTMProgram(
            states={"q0", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q0",
            halt_state="q_halt",
            transitions={("q0", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT)},
        )
        self.c_halt = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=1, history=(), step_count=0, halted=True)
        self.model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])

    def test_stage_audit(self) -> None:
        """Req 5 & 30: Stage audit matrix for Stages 1-8."""
        reports, ok = self.gate.audit_stage_matrix()
        self.assertTrue(ok)
        self.assertEqual(len(reports), 8)

    def test_full_module3_regression(self) -> None:
        """Req 6 & 30: Module 3 test suite execution baseline."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.test_audit["status"], "PASS")
        self.assertGreaterEqual(res.test_audit["passed"], 111)

    def test_end_to_end_pipeline(self) -> None:
        """Req 7 & 30: End-to-end integration audit across public component boundaries."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.integration_audit, Module3CompletionStatus.PASS)

    def test_mathematical_invariant_audit(self) -> None:
        """Req 9 & 30: Mathematical invariant audit (norm, orthogonality, U+ U = I)."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.invariant_audit, Module3CompletionStatus.PASS)

    def test_qtm_ir_validation_audit(self) -> None:
        """Req 10 & 30: QTM-IR validator audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.qtm_ir_audit, Module3CompletionStatus.PASS)

    def test_translator_audit(self) -> None:
        """Req 11 & 30: Translator T_RQ audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.translator_audit, Module3CompletionStatus.PASS)

    def test_execution_audit(self) -> None:
        """Req 12 & 30: Execution engine audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.execution_audit, Module3CompletionStatus.PASS)

    def test_equivalence_audit(self) -> None:
        """Req 13 & 30: Equivalence gate audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.equivalence_audit, Module3CompletionStatus.PASS)

    def test_negative_wrong_transition_detected(self) -> None:
        """Req 14 & 30: Negative test: wrong transition mapping detected."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.negative_path_audit, Module3CompletionStatus.PASS)

    def test_negative_wrong_basis_detected(self) -> None:
        """Req 14 & 30: Negative test: wrong basis identity detected."""
        c0_id = compute_canonical_basis_id(self.c_halt)
        modified_basis = dict(self.model.basis_states)
        modified_basis[c0_id] = QTMIRBasisState(basis_id=c0_id, current_state="q_wrong", tape={}, head_pos=99)
        mod_model = QTMIRModel(
            version=self.model.version,
            machine_id="mod",
            basis_states=modified_basis,
            initial_state_vector=self.model.initial_state_vector,
            transition_mapping=self.model.transition_mapping,
        )
        eq_res = verify_equivalence(self.utm_program, mod_model, initial_config=self.c_halt, max_steps=1)
        self.assertNotEqual(eq_res.status, EquivalenceStatus.PASS)

    def test_negative_extra_amplitude_detected(self) -> None:
        """Req 14 & 30: Negative test: extra spurious amplitude detected."""
        c0_id = compute_canonical_basis_id(self.c_halt)
        spurious_init = QTMIRStateVector(
            amplitudes={c0_id: QTMIRComplexNumber(0.6, 0.0), "extra_id": QTMIRComplexNumber(0.8, 0.0)}
        )
        spurious_model = QTMIRModel(
            version=self.model.version,
            machine_id="spurious",
            basis_states=self.model.basis_states,
            initial_state_vector=spurious_init,
            transition_mapping=self.model.transition_mapping,
        )
        eq_res = verify_equivalence(self.utm_program, spurious_model, initial_config=self.c_halt, max_steps=1)
        self.assertNotEqual(eq_res.status, EquivalenceStatus.PASS)

    def test_negative_domain_truncation_detected(self) -> None:
        """Req 14 & 30: Negative test: domain truncation produces INCONCLUSIVE."""
        c_other = RUTMConfiguration(current_state="q0", tape={0: "0"}, head_pos=0, history=(), step_count=0)
        trunc_model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        eq_res = verify_equivalence(self.utm_program, trunc_model, initial_config=c_other, max_steps=1)
        self.assertEqual(eq_res.status, EquivalenceStatus.INCONCLUSIVE)

    def test_history_integrity_audit(self) -> None:
        """Req 15 & 30: History integrity audit (H1 != H2 -> C1 != C2)."""
        h0 = HistoryRecord(prev_state="q0", overwritten_symbol="0", direction=Direction.RIGHT)
        c1 = RUTMConfiguration(current_state="q1", tape={0: "1"}, head_pos=1, history=(h0,), step_count=1)
        c2 = RUTMConfiguration(current_state="q1", tape={0: "1"}, head_pos=1, history=(), step_count=1)
        self.assertNotEqual(compute_canonical_basis_id(c1), compute_canonical_basis_id(c2))

    def test_halting_integrity_audit(self) -> None:
        """Req 16 & 30: Halting state is a unitary fixed point U_P|C_halt> = |C_halt>."""
        c_halt = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=1, history=(), step_count=0, halted=True)
        m_halt = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[c_halt])
        c_halt_id = compute_canonical_basis_id(c_halt)
        v_halt = QTMIRStateVector(amplitudes={c_halt_id: QTMIRComplexNumber(1.0, 0.0)})
        u_out = apply_unitary(m_halt, v_halt)
        self.assertEqual(u_out.amplitudes, v_halt.amplitudes)

    def test_error_integrity_audit(self) -> None:
        """Req 17 & 30: Error state is a unitary fixed point U_P|C_error> = |C_error>."""
        c_error = RUTMConfiguration(current_state="q0", tape={0: "1"}, head_pos=1, history=(), step_count=0, error="Test error")
        m_err = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[c_error])
        c_err_id = compute_canonical_basis_id(c_error)
        v_err = QTMIRStateVector(amplitudes={c_err_id: QTMIRComplexNumber(1.0, 0.0)})
        u_out = apply_unitary(m_err, v_err)
        self.assertEqual(u_out.amplitudes, v_err.amplitudes)

    def test_serialization_integrity_audit(self) -> None:
        """Req 18 & 30: Serialization JSON round-trip audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.serialization_audit, Module3CompletionStatus.PASS)

    def test_determinism_audit(self) -> None:
        """Req 19 & 30: Determinism audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.determinism_audit, Module3CompletionStatus.PASS)

    def test_provenance_audit(self) -> None:
        """Req 20 & 30: Provenance metadata & exact canonical relation audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.provenance_audit, Module3CompletionStatus.PASS)

    def test_public_api_audit(self) -> None:
        """Req 21 & 30: Public API export audit."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.public_api_audit, Module3CompletionStatus.PASS)

    def test_module4_boundary_audit(self) -> None:
        """Req 24 & 30: Module 4 project-phase-aware boundary audit (authorized post-Module 4 phase)."""
        res = self.gate.run_completion_gate()
        self.assertEqual(res.module4_boundary_audit, Module3CompletionStatus.PASS)
        self.assertEqual(res.overall_status, Module3CompletionStatus.PASS)

    def test_historical_pre_module4_boundary_audit(self) -> None:
        """Req 24 & 30: Historical pre-Module 4 boundary audit simulation (Module 4 code absent)."""
        orig_exists = os.path.exists
        def mock_exists(path: str) -> bool:
            if "src/module4" in path.replace("\\", "/"):
                return False
            return orig_exists(path)

        with unittest.mock.patch("os.path.exists", side_effect=mock_exists):
            res = self.gate.run_completion_gate()
            self.assertEqual(res.module4_boundary_audit, Module3CompletionStatus.PASS)
            self.assertEqual(res.overall_status, Module3CompletionStatus.PASS)

    def test_negative_corrupted_module4_boundary(self) -> None:
        """Negative test: Corrupted Module 4 boundary is detected by completion gate."""
        orig_isdir = os.path.isdir
        def mock_isdir(path: str) -> bool:
            if "src/module4" in path.replace("\\", "/"):
                return False
            return orig_isdir(path)

        with unittest.mock.patch("os.path.isdir", side_effect=mock_isdir):
            res = self.gate.run_completion_gate()
            self.assertEqual(res.module4_boundary_audit, Module3CompletionStatus.FAIL)
            self.assertEqual(res.overall_status, Module3CompletionStatus.FAIL)

    def test_negative_completion_gate_does_not_unconditionally_pass(self) -> None:
        """Negative test: Completion gate does not return unconditional PASS when Stage matrix fails."""
        with unittest.mock.patch.object(self.gate, "audit_stage_matrix", return_value=([], False)):
            res = self.gate.run_completion_gate()
            self.assertEqual(res.overall_status, Module3CompletionStatus.FAIL)



if __name__ == "__main__":
    unittest.main()

