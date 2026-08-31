"""
Unit Tests for Stage 11: Certificate C1 Generation & Validation.

Strictly compliant with Stage 11 requirements (main-technical-refference.md & STAGE_11_CERTIFICATE.md).
"""

import os
import json
import unittest
from typing import Dict

from src.module1.verification.dual import execute_dual_pipeline
from src.module1.verification.verifier import verify_semantic_equivalence
from src.module1.verification.certificate import (
    CertificateC1,
    generate_certificate_c1,
    serialize_certificate_c1,
    hash_certificate_c1,
    validate_certificate_c1,
    save_certificate_c1,
)


class TestStage11Certificate(unittest.TestCase):
    """Stage 11 Certificate C1 Generation & Validation Test Suite."""

    @classmethod
    def setUpClass(cls):
        """Golden PoC setup."""
        cls.golden_source = """
        LOAD R1, A
        LOAD R2, B
        ADD  R1, R2
        STORE OUT, R1
        HALT
"""
        cls.golden_memory = {"A": 5, "B": 7}
        cls.dual_res = execute_dual_pipeline(
            cls.golden_source, initial_memory=cls.golden_memory
        )
        cls.ver_res = verify_semantic_equivalence(cls.dual_res)
        cls.cert = generate_certificate_c1(
            cls.dual_res, cls.ver_res, input_state=cls.golden_memory, source_program_text=cls.golden_source
        )

    def test_1_golden_c1_generation(self):
        """Test 1: Golden PoC C1 generation and file persistence."""
        self.assertIsNotNone(self.cert)
        filepath = save_certificate_c1(self.cert, output_dir="certificates")
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".json"))

    def test_2_verified_status(self):
        """Test 2: VERIFIED status verification."""
        self.assertEqual(self.cert.identity["status"], "VERIFIED")
        self.assertTrue(self.cert.verification["verified"])

    def test_3_source_identity(self):
        """Test 3: Source identity sha256 hash and language metadata."""
        src = self.cert.source
        self.assertEqual(src["source_language"], "AML")
        self.assertEqual(src["source_language_version"], "v0.1")
        self.assertEqual(src["source_hash_algorithm"], "sha256")
        self.assertEqual(len(src["source_program_hash"]), 64)

    def test_4_aml_ir_identity(self):
        """Test 4: AML-IR identity evidence."""
        aml_ir = self.cert.aml_ir
        self.assertEqual(aml_ir["instruction_count"], 5)
        self.assertIn("A", aml_ir["symbol_table"])
        self.assertIn("OUT", aml_ir["symbol_table"])
        self.assertEqual(len(aml_ir["aml_ir_hash"]), 64)

    def test_5_utm_ir_identity(self):
        """Test 5: UTM-IR identity evidence."""
        utm_ir = self.cert.utm_ir
        self.assertGreater(utm_ir["state_count"], 0)
        self.assertGreater(utm_ir["transition_count"], 0)
        self.assertEqual(utm_ir["blank_symbol"], "_")
        self.assertEqual(utm_ir["initial_state"], "q_start")
        self.assertEqual(utm_ir["halt_state"], "q_halt")
        self.assertEqual(len(utm_ir["utm_ir_hash"]), 64)

    def test_6_translation_evidence(self):
        """Test 6: Translation evidence section."""
        trans = self.cert.translation
        self.assertEqual(trans["translation_status"], "TRANSLATION_GENERATED")
        self.assertTrue(trans["deterministic_translation"])
        self.assertTrue(trans["generated_utm_valid"])

    def test_7_execution_evidence(self):
        """Test 7: Execution evidence section."""
        exec_ev = self.cert.execution
        self.assertEqual(exec_ev["aml_status"], "SUCCESS")
        self.assertTrue(exec_ev["aml_halted"])
        self.assertGreater(exec_ev["aml_step_count"], 0)
        self.assertEqual(exec_ev["utm_status"], "SUCCESS")
        self.assertTrue(exec_ev["utm_halted"])
        self.assertGreater(exec_ev["utm_step_count"], 0)

    def test_8_observation_evidence(self):
        """Test 8: Preservation of exact Obs_AML and Obs_UTM memory observations."""
        obs = self.cert.observation
        expected_memory = {"A": 5, "B": 7, "OUT": 12}
        self.assertEqual(obs["Obs_AML"], expected_memory)
        self.assertEqual(obs["Obs_UTM"], expected_memory)

    def test_9_halting_evidence(self):
        """Test 9: Halting evidence."""
        self.assertTrue(self.cert.execution["aml_halted"])
        self.assertTrue(self.cert.execution["utm_halted"])
        self.assertTrue(self.cert.verification["halting_equal"])

    def test_10_empirical_scope(self):
        """Test 10: Empirical scope limitation."""
        self.assertEqual(self.cert.claims["verification_scope"], "SINGLE_EXECUTION_INSTANCE")
        self.assertEqual(self.cert.scope["scope"], "SINGLE_EXECUTION_INSTANCE")

    def test_11_universal_claim_false(self):
        """Test 11: CRITICAL SCIENTIFIC REQUIREMENT - universal_claim MUST be False."""
        self.assertFalse(self.cert.claims["universal_claim"])

    def test_12_formal_proof_false(self):
        """Test 12: CRITICAL SCIENTIFIC REQUIREMENT - formal_proof MUST be False."""
        self.assertFalse(self.cert.claims["formal_proof"])

    def test_13_certificate_validation_positive(self):
        """Test 13: Positive self-consistency validation of golden C1."""
        is_valid, err = validate_certificate_c1(self.cert)
        self.assertTrue(is_valid, f"Validation failed with error: {err}")
        self.assertIsNone(err)

    def test_14_deterministic_serialization(self):
        """Test 14: Deterministic canonical JSON serialization."""
        str1 = serialize_certificate_c1(self.cert)
        str2 = serialize_certificate_c1(self.cert)
        self.assertEqual(str1, str2)

    def test_15_deterministic_certificate_hash(self):
        """Test 15: Deterministic certificate SHA-256 hash."""
        h1 = hash_certificate_c1(self.cert)
        h2 = hash_certificate_c1(self.cert)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_16_output_mismatch_rejection(self):
        """Test 16: Negative test - Output mismatch rejected by validator."""
        corrupted_cert = self.cert.to_dict()
        corrupted_cert["observation"]["Obs_UTM"]["OUT"] = 99  # Mismatch!
        corrupted_cert["certificate_hash"] = hash_certificate_c1(corrupted_cert)

        is_valid, err = validate_certificate_c1(corrupted_cert)
        self.assertFalse(is_valid)
        self.assertIn("Obs_AML != Obs_UTM", err)

    def test_17_halting_mismatch_rejection(self):
        """Test 17: Negative test - Halting mismatch rejected by validator."""
        corrupted_cert = self.cert.to_dict()
        corrupted_cert["execution"]["utm_halted"] = False  # Halting mismatch!
        corrupted_cert["certificate_hash"] = hash_certificate_c1(corrupted_cert)

        is_valid, err = validate_certificate_c1(corrupted_cert)
        self.assertFalse(is_valid)
        self.assertIn("utm_halted is False", err)

    def test_18_invalid_translation_rejection(self):
        """Test 18: Negative test - Invalid translation status rejection."""
        corrupted_cert = self.cert.to_dict()
        corrupted_cert["identity"]["status"] = "INVALID_TRANSLATION"
        corrupted_cert["verification"]["verified"] = True  # Inconsistent!
        corrupted_cert["certificate_hash"] = hash_certificate_c1(corrupted_cert)

        is_valid, err = validate_certificate_c1(corrupted_cert)
        self.assertFalse(is_valid)
        self.assertIn("Inconsistent certificate", err)

    def test_19_resource_limit_rejection(self):
        """Test 19: Negative test - RESOURCE_LIMIT status with verified=True rejection."""
        corrupted_cert = self.cert.to_dict()
        corrupted_cert["identity"]["status"] = "RESOURCE_LIMIT"
        corrupted_cert["verification"]["verified"] = True  # Inconsistent!
        corrupted_cert["certificate_hash"] = hash_certificate_c1(corrupted_cert)

        is_valid, err = validate_certificate_c1(corrupted_cert)
        self.assertFalse(is_valid)
        self.assertIn("Inconsistent certificate", err)

    def test_20_corrupted_certificate_rejection(self):
        """Test 20: Negative test - Tampered payload hash rejection."""
        corrupted_cert = self.cert.to_dict()
        original_hash = corrupted_cert["certificate_hash"]
        corrupted_cert["provenance"]["compiler_version"] = "99.9"  # Tampered field
        corrupted_cert["certificate_hash"] = original_hash  # Hash un-updated!

        is_valid, err = validate_certificate_c1(corrupted_cert)
        self.assertFalse(is_valid)
        self.assertIn("Corrupted certificate: hash mismatch", err)

    def test_21_certificate_reproducibility(self):
        """Test 21: Scientific reproducibility across separate dual execution runs."""
        dual_1 = execute_dual_pipeline(self.golden_source, initial_memory=self.golden_memory)
        ver_1 = verify_semantic_equivalence(dual_1)
        cert_1 = generate_certificate_c1(dual_1, ver_1, input_state=self.golden_memory, source_program_text=self.golden_source)

        dual_2 = execute_dual_pipeline(self.golden_source, initial_memory=self.golden_memory)
        ver_2 = verify_semantic_equivalence(dual_2)
        cert_2 = generate_certificate_c1(dual_2, ver_2, input_state=self.golden_memory, source_program_text=self.golden_source)

        self.assertEqual(serialize_certificate_c1(cert_1), serialize_certificate_c1(cert_2))
        self.assertEqual(hash_certificate_c1(cert_1), hash_certificate_c1(cert_2))


if __name__ == "__main__":
    unittest.main()
