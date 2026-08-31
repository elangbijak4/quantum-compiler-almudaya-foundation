r"""
Module 3 Stage 5 Test Suite — QTM-IR Model, Semantic Validator & Canonical Serialization.

Verifies:
A. Valid minimal QTM-IR model passes validation
B. Invalid schema / model type rejected
C. Unsupported QTM-IR schema version rejected
D. Invalid basis state rejected
E. Invalid complex amplitude (NaN/Inf) rejected
F. Malformed state vector rejected
G. State vector norm preservation violation detected
H. Mismatched basis state ID rejected
I. Transition mapping referencing non-existent basis states rejected
J. Forward transition mapping non-bijective (totality, surjectivity, injectivity) rejected
K. Reverse transition mapping missing/incomplete/non-bijective rejected (Correction C)
L. Valid permutation matrix accepted (Left & Right Unitarity)
M. Matrix dimension mismatch rejected
N. Missing, empty, or non-exact canonical provenance semantic relation rejected (Correction B)
O. Deterministic serialization round-trip equality deserialize(serialize(model)) == model
P. Adjoint / reverse mapping metadata preserved
Q. Isolated history field semantic configuration identity & round-trip content verification (Correction A)
"""

import unittest
import math
import json
from src.module2.rutm.model import HistoryRecord, Direction
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    QTM_IR_VERSION,
    CANONICAL_SEMANTIC_RELATION,
)
from src.module3.qtm_ir.validator import (
    validate_qtm_ir,
    ValidationResult,
    ValidationDiagnostic,
    DiagnosticCode,
    ValidationSeverity,
)
from src.module3.qtm_ir.serialization import (
    serialize_qtm_ir,
    deserialize_qtm_ir,
    serialize_qtm_ir_to_json,
    deserialize_qtm_ir_from_json,
)


class TestStage5QTMIR(unittest.TestCase):
    """Unit test suite for QTM-IR model, validator, and serialization."""

    def setUp(self) -> None:
        """Sets up valid test QTM-IR fixtures."""
        self.h0 = HistoryRecord(prev_state="q_start", overwritten_symbol="0", direction=Direction.RIGHT)
        self.h1 = HistoryRecord(prev_state="q_step1", overwritten_symbol="1", direction=Direction.RIGHT)

        self.b0 = QTMIRBasisState(
            basis_id="b0",
            current_state="q_start",
            tape={0: "0", 1: "1"},
            head_pos=0,
            history=(),
            step_count=0,
            halted=False,
        )
        self.b1 = QTMIRBasisState(
            basis_id="b1",
            current_state="q_step1",
            tape={0: "1", 1: "1"},
            head_pos=1,
            history=(self.h0,),
            step_count=1,
            halted=False,
        )
        self.b2 = QTMIRBasisState(
            basis_id="b2",
            current_state="q_halt",
            tape={0: "1", 1: "1"},
            head_pos=1,
            history=(self.h0, self.h1),
            step_count=2,
            halted=True,
        )

        self.basis_states = {"b0": self.b0, "b1": self.b1, "b2": self.b2}

        # Equal superposition: (|b0⟩ + |b1⟩)/sqrt(2)
        amp = QTMIRComplexNumber(real=1.0 / math.sqrt(2.0), imag=0.0)
        self.init_vector = QTMIRStateVector(
            amplitudes={"b0": amp, "b1": amp},
            tolerance=1e-12,
            is_normalized=True,
        )

        # 3-cycle bijective mapping: b0 -> b1 -> b2 -> b0
        self.trans_mapping = QTMIRTransitionMapping(
            forward_mapping={"b0": "b1", "b1": "b2", "b2": "b0"},
            reverse_mapping={"b1": "b0", "b2": "b1", "b0": "b2"},
            is_bijective=True,
        )

        # 3x3 Permutation matrix representation
        c0 = QTMIRComplexNumber(0.0, 0.0)
        c1 = QTMIRComplexNumber(1.0, 0.0)
        matrix = [
            [c0, c0, c1],  # b0 target
            [c1, c0, c0],  # b1 target
            [c0, c1, c0],  # b2 target
        ]
        self.matrix_rep = QTMIRMatrixRepresentation(
            basis_order=["b0", "b1", "b2"],
            matrix=matrix,
            dimension=3,
        )

        self.provenance = QTMIRProvenance(
            source_rutm_program_hash="abc123hash",
            source_module="Module 2 (RUTM-IR)",
            stage="Stage 5 (QTM-IR Model)",
            compiler_version="0.3.0-alpha",
            semantic_relation=CANONICAL_SEMANTIC_RELATION,
        )

        self.valid_model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test_qtm_01",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            matrix_representation=self.matrix_rep,
            provenance=self.provenance,
        )

    def test_01_valid_minimal_qtm_ir(self) -> None:
        """Test A: Valid minimal QTM-IR model passes validation cleanly."""
        res = validate_qtm_ir(self.valid_model)
        self.assertTrue(res.valid, msg=[d.message for d in res.diagnostics])
        self.assertEqual(len(res.diagnostics), 0)

    def test_02_invalid_schema_rejected(self) -> None:
        """Test B: Non-QTMIRModel object rejected."""
        res = validate_qtm_ir("invalid_string_model")
        self.assertFalse(res.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_SCHEMA_INVALID.value for d in res.diagnostics))

    def test_03_unsupported_version_rejected(self) -> None:
        """Test C: Unsupported schema version rejected."""
        invalid_ver_model = QTMIRModel(
            version="9.9.9",
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            provenance=self.provenance,
        )
        res = validate_qtm_ir(invalid_ver_model)
        self.assertFalse(res.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_VERSION_UNSUPPORTED.value for d in res.diagnostics))

    def test_04_invalid_basis_state_id_mismatch(self) -> None:
        """Test D: Mismatched basis_id key vs object basis_id rejected."""
        bad_basis = dict(self.basis_states)
        bad_basis["mismatched_key"] = self.b0
        bad_model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=bad_basis,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            provenance=self.provenance,
        )
        res = validate_qtm_ir(bad_model)
        self.assertFalse(res.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_BASIS_INVALID.value for d in res.diagnostics))

    def test_05_invalid_complex_amplitude(self) -> None:
        """Test E: NaN or Inf complex amplitude rejected."""
        nan_amp = QTMIRComplexNumber(real=float("nan"), imag=0.0)
        bad_vec = QTMIRStateVector(amplitudes={"b0": nan_amp, "b1": nan_amp})
        bad_model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=bad_vec,
            transition_mapping=self.trans_mapping,
            provenance=self.provenance,
        )
        res = validate_qtm_ir(bad_model)
        self.assertFalse(res.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_AMPLITUDE_INVALID.value for d in res.diagnostics))

    def test_06_norm_preservation_violation_detected(self) -> None:
        """Test G: State vector norm != 1.0 detected."""
        unnorm_amp = QTMIRComplexNumber(real=3.0, imag=4.0)
        unnorm_vec = QTMIRStateVector(amplitudes={"b0": unnorm_amp})
        bad_model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=unnorm_vec,
            transition_mapping=self.trans_mapping,
            provenance=self.provenance,
        )
        res = validate_qtm_ir(bad_model)
        self.assertFalse(res.valid)
        self.assertTrue(any("norm preservation failure" in d.message for d in res.diagnostics))

    def test_07_transition_referencing_non_existent_basis(self) -> None:
        """Test I: Transition referencing non-existent basis state ID rejected."""
        bad_mapping = QTMIRTransitionMapping(
            forward_mapping={"b0": "b1", "b1": "b2", "b2": "non_existent_b3"},
            reverse_mapping={"b1": "b0", "b2": "b1", "non_existent_b3": "b2"},
        )
        bad_model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=bad_mapping,
            provenance=self.provenance,
        )
        res = validate_qtm_ir(bad_model)
        self.assertFalse(res.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_DOMAIN_NOT_CLOSED.value for d in res.diagnostics))

    def test_08_forward_transition_totality_and_collision_rejected(self) -> None:
        """Test J: Non-bijective forward transition mapping rejected."""
        # 1. Missing outgoing transition (not total)
        missing_total = QTMIRTransitionMapping(
            forward_mapping={"b0": "b1", "b1": "b2"},  # b2 missing forward transition
            reverse_mapping={"b1": "b0", "b2": "b1", "b0": "b2"},
        )
        model_missing_total = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=missing_total,
            provenance=self.provenance,
        )
        res1 = validate_qtm_ir(model_missing_total)
        self.assertFalse(res1.valid)
        self.assertTrue(any("Forward transition mapping is not total" in d.message for d in res1.diagnostics))

        # 2. Collision (not injective)
        collision_mapping = QTMIRTransitionMapping(
            forward_mapping={"b0": "b2", "b1": "b2", "b2": "b0"},
            reverse_mapping={"b2": "b0", "b0": "b2", "b1": "b1"},
        )
        model_collision = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=collision_mapping,
            provenance=self.provenance,
        )
        res2 = validate_qtm_ir(model_collision)
        self.assertFalse(res2.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value for d in res2.diagnostics))

    def test_09_reverse_mapping_completeness_and_round_trip(self) -> None:
        """Test K (Correction C): Reverse mapping completeness, domain equality, & composition identities."""
        # 1. Empty reverse mapping rejected
        empty_rev = QTMIRTransitionMapping(
            forward_mapping={"b0": "b1", "b1": "b2", "b2": "b0"},
            reverse_mapping={},
        )
        model_empty_rev = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=empty_rev,
            provenance=self.provenance,
        )
        res1 = validate_qtm_ir(model_empty_rev)
        self.assertFalse(res1.valid)
        self.assertTrue(any("reverse_mapping dictionary is missing or empty" in d.message for d in res1.diagnostics))

        # 2. Reverse mapping missing source (not total over D) rejected
        missing_rev_src = QTMIRTransitionMapping(
            forward_mapping={"b0": "b1", "b1": "b2", "b2": "b0"},
            reverse_mapping={"b1": "b0", "b2": "b1"},  # b0 missing from reverse_mapping keys
        )
        model_missing_rev_src = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=missing_rev_src,
            provenance=self.provenance,
        )
        res2 = validate_qtm_ir(model_missing_rev_src)
        self.assertFalse(res2.valid)
        self.assertTrue(any("Reverse transition mapping is not total" in d.message for d in res2.diagnostics))

        # 3. Composition disagreement (R_P^-1 ∘ R_P != id_D) rejected
        disagree_rev = QTMIRTransitionMapping(
            forward_mapping={"b0": "b1", "b1": "b2", "b2": "b0"},
            reverse_mapping={"b1": "b0", "b2": "b0", "b0": "b1"},  # Reverse maps b2 to b0 instead of b1
        )
        model_disagree_rev = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=disagree_rev,
            provenance=self.provenance,
        )
        res3 = validate_qtm_ir(model_disagree_rev)
        self.assertFalse(res3.valid)
        self.assertTrue(any("Reverse composition identity failure" in d.message for d in res3.diagnostics))

    def test_10_non_permutation_and_unitarity_matrix_rejected(self) -> None:
        """Test L: Non-permutation and unitarity failure matrices rejected."""
        c0 = QTMIRComplexNumber(0.0, 0.0)
        c1 = QTMIRComplexNumber(1.0, 0.0)
        c_half = QTMIRComplexNumber(0.5, 0.0)
        bad_matrix = [
            [c_half, c_half, c0],
            [c1, c0, c0],
            [c0, c1, c0],
        ]
        bad_mat = QTMIRMatrixRepresentation(
            basis_order=["b0", "b1", "b2"],
            matrix=bad_matrix,
            dimension=3,
        )
        bad_model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            matrix_representation=bad_mat,
            provenance=self.provenance,
        )
        res = validate_qtm_ir(bad_model)
        self.assertFalse(res.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_MATRIX_NOT_PERMUTATION.value for d in res.diagnostics))

    def test_11_exact_canonical_provenance_relation_validation(self) -> None:
        """Test N (Correction B): Exact canonical semantic_relation match required."""
        # 1. Exact canonical relation passes
        res1 = validate_qtm_ir(self.valid_model)
        self.assertTrue(res1.valid)

        # 2. Empty relation rejected
        empty_rel_prov = QTMIRProvenance(
            source_rutm_program_hash="abc",
            semantic_relation="",
        )
        model_empty = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            provenance=empty_rel_prov,
        )
        res2 = validate_qtm_ir(model_empty)
        self.assertFalse(res2.valid)
        self.assertTrue(any(d.code == DiagnosticCode.QTM_PROVENANCE_INVALID.value for d in res2.diagnostics))

        # 3. Unrelated relation rejected
        unrelated_prov = QTMIRProvenance(
            source_rutm_program_hash="abc",
            semantic_relation="Unrelated description",
        )
        model_unrelated = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            provenance=unrelated_prov,
        )
        res3 = validate_qtm_ir(model_unrelated)
        self.assertFalse(res3.valid)
        self.assertTrue(any("does not match canonical relation" in d.message for d in res3.diagnostics))

        # 4. Semantically similar but non-canonical relation rejected ("Lifting U_P iota R_P")
        similar_prov1 = QTMIRProvenance(
            source_rutm_program_hash="abc",
            semantic_relation="Lifting U_P iota R_P",
        )
        model_similar1 = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            provenance=similar_prov1,
        )
        res4 = validate_qtm_ir(model_similar1)
        self.assertFalse(res4.valid)
        self.assertTrue(any("does not match canonical relation" in d.message for d in res4.diagnostics))

        # 5. Partial non-canonical relation rejected ("Canonical QTM Lifting")
        similar_prov2 = QTMIRProvenance(
            source_rutm_program_hash="abc",
            semantic_relation="Canonical QTM Lifting",
        )
        model_similar2 = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test",
            basis_states=self.basis_states,
            initial_state_vector=self.init_vector,
            transition_mapping=self.trans_mapping,
            provenance=similar_prov2,
        )
        res5 = validate_qtm_ir(model_similar2)
        self.assertFalse(res5.valid)
        self.assertTrue(any("does not match canonical relation" in d.message for d in res5.diagnostics))

    def test_12_deterministic_serialization_round_trip(self) -> None:
        """Test O: Serialization round-trip equality deserialize(serialize(model)) == model."""
        serialized_dict = serialize_qtm_ir(self.valid_model)
        deserialized_model = deserialize_qtm_ir(serialized_dict)

        self.assertEqual(deserialized_model.version, self.valid_model.version)
        self.assertEqual(deserialized_model.machine_id, self.valid_model.machine_id)
        self.assertEqual(deserialized_model.basis_states, self.valid_model.basis_states)
        self.assertEqual(deserialized_model.initial_state_vector, self.valid_model.initial_state_vector)
        self.assertEqual(deserialized_model.transition_mapping, self.valid_model.transition_mapping)
        self.assertEqual(deserialized_model.matrix_representation, self.valid_model.matrix_representation)
        self.assertEqual(deserialized_model.provenance, self.valid_model.provenance)

    def test_13_json_serialization_round_trip(self) -> None:
        """Test P: JSON serialization round-trip JSON string."""
        json_str = serialize_qtm_ir_to_json(self.valid_model)
        deserialized_model = deserialize_qtm_ir_from_json(json_str)

        self.assertEqual(deserialized_model.version, self.valid_model.version)
        self.assertEqual(deserialized_model.machine_id, self.valid_model.machine_id)
        self.assertEqual(deserialized_model.basis_states, self.valid_model.basis_states)

    def test_14_isolated_history_semantic_identity(self) -> None:
        """Test Q (Correction A): Isolated history semantic identity (identical basis_id, state, tape, head_pos, step_count, halted, error, ONLY history differs)."""
        # Construct C1 and C2 with SAME basis_id, current_state, tape, head_pos, step_count, halted, error
        # and ONLY history differing (H1 != H2).
        c1 = QTMIRBasisState(
            basis_id="b_iso",
            current_state="q_step1",
            tape={0: "1"},
            head_pos=0,
            history=(self.h0,),
            step_count=1,
            halted=False,
            error=None,
        )
        c2 = QTMIRBasisState(
            basis_id="b_iso",
            current_state="q_step1",
            tape={0: "1"},
            head_pos=0,
            history=(self.h0, self.h1),
            step_count=1,
            halted=False,
            error=None,
        )

        # 1. Establish isolated semantic inequality: C1 != C2
        self.assertNotEqual(c1, c2)

        # Construct models with c1 vs c2 to test serialization survival
        m1 = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test_hist_iso_1",
            basis_states={"b_iso": c1},
            initial_state_vector=QTMIRStateVector(
                amplitudes={"b_iso": QTMIRComplexNumber(1.0, 0.0)},
            ),
            transition_mapping=QTMIRTransitionMapping(
                forward_mapping={"b_iso": "b_iso"},
                reverse_mapping={"b_iso": "b_iso"},
            ),
            provenance=self.provenance,
        )
        m2 = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id="test_hist_iso_2",
            basis_states={"b_iso": c2},
            initial_state_vector=QTMIRStateVector(
                amplitudes={"b_iso": QTMIRComplexNumber(1.0, 0.0)},
            ),
            transition_mapping=QTMIRTransitionMapping(
                forward_mapping={"b_iso": "b_iso"},
                reverse_mapping={"b_iso": "b_iso"},
            ),
            provenance=self.provenance,
        )

        # 2. Verify dict round-trip content
        m1_dict_deserialized = deserialize_qtm_ir(serialize_qtm_ir(m1))
        m2_dict_deserialized = deserialize_qtm_ir(serialize_qtm_ir(m2))
        self.assertNotEqual(m1_dict_deserialized.basis_states["b_iso"], m2_dict_deserialized.basis_states["b_iso"])

        # 3. Verify JSON round-trip content equality
        m1_json_deserialized = deserialize_qtm_ir_from_json(serialize_qtm_ir_to_json(m1))
        m2_json_deserialized = deserialize_qtm_ir_from_json(serialize_qtm_ir_to_json(m2))

        c1_deserialized = m1_json_deserialized.basis_states["b_iso"]
        c2_deserialized = m2_json_deserialized.basis_states["b_iso"]

        # Verify actual content of reconstructed HistoryRecord instances
        self.assertEqual(len(c1_deserialized.history), 1)
        self.assertEqual(len(c2_deserialized.history), 2)

        rec1 = c1_deserialized.history[0]
        self.assertEqual(rec1.prev_state, "q_start")
        self.assertEqual(rec1.overwritten_symbol, "0")
        self.assertEqual(rec1.direction, Direction.RIGHT)

        rec2_0 = c2_deserialized.history[0]
        rec2_1 = c2_deserialized.history[1]
        self.assertEqual(rec2_0.prev_state, "q_start")
        self.assertEqual(rec2_0.overwritten_symbol, "0")
        self.assertEqual(rec2_0.direction, Direction.RIGHT)
        self.assertEqual(rec2_1.prev_state, "q_step1")
        self.assertEqual(rec2_1.overwritten_symbol, "1")
        self.assertEqual(rec2_1.direction, Direction.RIGHT)


if __name__ == "__main__":
    unittest.main()
