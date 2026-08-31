"""
Unit Tests for Module 2 Stage 9: Self-Auditing Completion / Integration Gate.

Strictly compliant with Stage 9 requirements (main-technical-refference.md & STAGE_9_MODULE_2_COMPLETION.md).
"""

import os
import tempfile
import unittest
from src.module2.completion.gate import (
    verify_module2_completion,
    _audit_stage_inventory,
    _audit_implementation_packages,
    _audit_canonical_ownership,
    _audit_duplicate_semantics,
    _audit_proof_boundary,
    _audit_certificate_boundary,
    _audit_quantum_boundary,
    _audit_documentation_portability,
    _audit_documentation_links,
    _audit_import_health,
)


class TestStage9SelfAuditingCompletionGate(unittest.TestCase):
    """Stage 9 Self-Auditing Module 2 Completion / Integration Gate Test Suite."""

    @classmethod
    def setUpClass(cls):
        """Run the completion gate once for the test class."""
        cls.completion_res = verify_module2_completion()

    def test_1_stage_inventory_audit_passes(self):
        """Test 1: Stage inventory audit passes on the real repository."""
        ok, stage_map, errs = _audit_stage_inventory()
        self.assertTrue(ok)
        self.assertEqual(len(stage_map), 8)
        self.assertEqual(len(errs), 0)

    def test_2_missing_stage_document_detected(self):
        """Test 2: Missing required stage document is detected without damaging real repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = os.path.join(tmpdir, "docs", "module-2")
            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(docs_dir, exist_ok=True)
            os.makedirs(src_dir, exist_ok=True)
            # Create only Stage 1, leaving Stage 2-8 missing
            with open(os.path.join(docs_dir, "STAGE_1_RUTM_SPECIFICATION.md"), "w") as f:
                f.write("Stage 1 spec")

            ok, stage_map, errs = _audit_stage_inventory(repo_root=tmpdir)
            self.assertFalse(ok)
            self.assertFalse(stage_map["Stage 2 — RUTM Configuration Model"])
            self.assertGreater(len(errs), 0)

    def test_3_required_implementation_packages_exist(self):
        """Test 3: Required implementation packages audit passes on current repo."""
        ok, errs = _audit_implementation_packages()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_4_canonical_imports_succeed(self):
        """Test 4: Canonical imports audit passes."""
        ok, errs = _audit_canonical_ownership()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_5_documentation_portable_links_pass(self):
        """Test 5: Documentation portable-link audit passes on real repo."""
        ok, errs = _audit_documentation_portability()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_6_broken_relative_link_detectable(self):
        """Test 6: Broken relative documentation link is detectable without damaging real repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = os.path.join(tmpdir, "docs", "module-2")
            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(docs_dir, exist_ok=True)
            os.makedirs(src_dir, exist_ok=True)

            with open(os.path.join(docs_dir, "test_doc.md"), "w") as f:
                f.write("Link to [missing](NON_EXISTENT_FILE.md)")

            ok, errs = _audit_documentation_links(repo_root=tmpdir)
            self.assertFalse(ok)
            self.assertGreater(len(errs), 0)
            self.assertIn("NON_EXISTENT_FILE.md", errs[0])

    def test_7_proof_boundary_audit_passes(self):
        """Test 7: Proof boundary audit passes on real repo."""
        ok, errs = _audit_proof_boundary()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_8_certificate_boundary_audit_passes(self):
        """Test 8: Certificate boundary audit passes on real repo."""
        ok, errs = _audit_certificate_boundary()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_9_quantum_boundary_audit_passes(self):
        """Test 9: Quantum boundary audit passes on real repo."""
        ok, errs = _audit_quantum_boundary()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_10_duplicate_semantics_audit_passes(self):
        """Test 10: Duplicate semantics audit passes on current repository."""
        ok, errs = _audit_duplicate_semantics()
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_11_runtime_regression_remains_pass(self):
        """Test 11: Module 1 & Module 2 runtime regressions remain PASS."""
        self.assertTrue(self.completion_res.regression_verified)
        self.assertGreaterEqual(self.completion_res.module2_test_count, 140)
        self.assertGreaterEqual(self.completion_res.module1_test_count, 79)

    def test_12_golden_pipeline_remains_pass(self):
        """Test 12: End-to-end golden pipeline remains PASS."""
        self.assertTrue(self.completion_res.end_to_end_verified)

    def test_13_reversibility_remains_pass(self):
        """Test 13: Reversibility verification remains PASS."""
        self.assertTrue(self.completion_res.reversibility_verified)

    def test_14_equivalence_remains_pass(self):
        """Test 14: UTM -> RUTM equivalence gate remains PASS."""
        self.assertTrue(self.completion_res.equivalence_verified)

    def test_15_final_completion_result_is_complete(self):
        """Test 15: Final completion result is COMPLETE with self-auditing enabled."""
        self.assertEqual(self.completion_res.status, "COMPLETE")
        self.assertTrue(self.completion_res.audit_results.get("stage_inventory"))
        self.assertTrue(self.completion_res.audit_results.get("implementation_packages"))
        self.assertTrue(self.completion_res.audit_results.get("canonical_ownership"))
        self.assertTrue(self.completion_res.audit_results.get("duplicate_semantics"))
        self.assertTrue(self.completion_res.audit_results.get("proof_boundary"))
        self.assertTrue(self.completion_res.audit_results.get("certificate_boundary"))
        self.assertTrue(self.completion_res.audit_results.get("quantum_boundary"))
        self.assertTrue(self.completion_res.audit_results.get("documentation_portability"))
        self.assertTrue(self.completion_res.audit_results.get("documentation_links"))
        self.assertTrue(self.completion_res.audit_results.get("import_health"))


if __name__ == "__main__":
    unittest.main()
