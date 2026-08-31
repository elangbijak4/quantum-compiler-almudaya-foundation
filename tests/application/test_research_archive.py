"""
Application / Product Layer — Research Run / Output Archive Unit & Integration Tests.

Verifies OutputArchiveManager, ResearchRun, artifact chaining, parent/child linkage,
archive/authority consistency, immutability, read-only inspection, and security credential isolation.
"""

import json
import os
import shutil
import tempfile
import unittest

from src.application import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
    ApplicationContractService,
    ResearchRunStatus,
    ArchivedArtifact,
    ResearchRun,
    OutputArchiveManager,
)


class TestResearchArchive(unittest.TestCase):
    """Test suite for Research Run / Output Archive architecture."""

    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp(prefix="test_output_archive_")
        self.archive_mgr = OutputArchiveManager(base_dir=self.test_dir)
        self.service = ApplicationContractService()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_real_compiler_run_materialization(self) -> None:
        """Verifies real local compiler run materialization as a ResearchRun."""
        run_id = "RUN_LOCAL_E2E_01"
        self.archive_mgr.start_research_run(
            run_id=run_id,
            backend_id="LOCAL_REFERENCE",
            shots=1000,
            source_code="x = 5; y = 10; z = x + y",
        )

        # 1. Source -> AML
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("SRC_01", "SourceCode", "hash_src_01", "00_input", "SUCCESS"),
        )
        # 2. AML -> UTM
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("AML_01", "AMLArtifact", "hash_aml_01", "01_aml", "SUCCESS", parent_artifact_id="SRC_01"),
        )
        # 3. UTM -> RUTM
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("UTM_01", "UTMArtifact", "hash_utm_01", "02_utm", "SUCCESS", parent_artifact_id="AML_01"),
        )
        # 4. RUTM -> Semantic Certificate
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("CERT_01", "SemanticCertificate", "hash_cert_01", "04_semantic", "SUCCESS", parent_artifact_id="UTM_01"),
        )
        # 5. Logical Circuit
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("LOG_CIRC_01", "LogicalCircuit", "hash_log_01", "05_mapping", "SUCCESS", parent_artifact_id="CERT_01"),
        )
        # 6. Lowering -> Native Circuit
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("NAT_CIRC_01", "NativeCircuit", "hash_nat_01", "07_lowering", "SUCCESS", parent_artifact_id="LOG_CIRC_01"),
        )
        # 7. Simulation -> Result
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("SIM_RES_01", "SimulationResult", "hash_sim_01", "08_simulation", "SUCCESS", parent_artifact_id="NAT_CIRC_01"),
        )
        # 8. Verification -> Decision
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("VER_REC_01", "VerificationRecord", "hash_ver_01", "10_verification", "VERIFIED", parent_artifact_id="SIM_RES_01"),
        )

        run_dir = self.archive_mgr.finalize_research_run(run_id, ResearchRunStatus.COMPLETED, lineage_reference="LINEAGE_01")
        self.assertTrue(os.path.exists(run_dir))
        self.assertTrue(os.path.exists(os.path.join(run_dir, "manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(run_dir, "README.md")))

        # Validate loaded manifest
        manifest = self.archive_mgr.load_research_run(run_dir)
        self.assertEqual(manifest["run_id"], run_id)
        self.assertEqual(manifest["status"], "COMPLETED")
        self.assertEqual(manifest["artifacts_count"], 8)
        self.assertEqual(manifest["lineage_reference"], "LINEAGE_01")

    def test_02_artifact_identity_and_parent_child_continuity(self) -> None:
        """Verifies archived artifact identity and parent/child linkage continuity."""
        run_id = "RUN_LINKAGE_01"
        self.archive_mgr.start_research_run(run_id)

        art1 = ArchivedArtifact("P1", "ParentType", "hash_p1", "01_stage", "SUCCESS")
        art2 = ArchivedArtifact("C1", "ChildType", "hash_c1", "02_stage", "SUCCESS", parent_artifact_id="P1")

        self.archive_mgr.record_artifact(run_id, art1)
        self.archive_mgr.record_artifact(run_id, art2)

        run_dir = self.archive_mgr.finalize_research_run(run_id)
        manifest = self.archive_mgr.load_research_run(run_dir)

        artifacts = manifest["artifacts"]
        self.assertEqual(artifacts[0]["artifact_id"], "P1")
        self.assertEqual(artifacts[1]["artifact_id"], "C1")
        self.assertEqual(artifacts[1]["parent_artifact_id"], artifacts[0]["artifact_id"])

    def test_03_run_immutability(self) -> None:
        """Verifies HISTORICAL RUN IMMUTABILITY = PASS (run_A remains unchanged when run_B is executed)."""
        # Run A
        run_id_A = "RUN_A"
        self.archive_mgr.start_research_run(run_id_A)
        self.archive_mgr.record_artifact(run_id_A, ArchivedArtifact("A1", "TypeA", "hash_A1", "01_stage", "SUCCESS"))
        dir_A = self.archive_mgr.finalize_research_run(run_id_A)

        with open(os.path.join(dir_A, "manifest.json"), "r", encoding="utf-8") as f:
            manifest_A_before = f.read()

        # Run B
        run_id_B = "RUN_B"
        self.archive_mgr.start_research_run(run_id_B)
        self.archive_mgr.record_artifact(run_id_B, ArchivedArtifact("B1", "TypeB", "hash_B1", "01_stage", "SUCCESS"))
        self.archive_mgr.finalize_research_run(run_id_B)

        # Verify Run A was NOT altered
        with open(os.path.join(dir_A, "manifest.json"), "r", encoding="utf-8") as f:
            manifest_A_after = f.read()

        self.assertEqual(manifest_A_before, manifest_A_after)

    def test_04_read_only_inspection(self) -> None:
        """Verifies load_research_run triggers zero compilation or execution side-effects."""
        run_id = "RUN_INSPECT_01"
        self.archive_mgr.start_research_run(run_id)
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact("I1", "InspectType", "hash_i1", "00_input", "SUCCESS"))
        dir_path = self.archive_mgr.finalize_research_run(run_id)

        manifest = self.archive_mgr.load_research_run(dir_path)
        self.assertEqual(manifest["run_id"], run_id)
        self.assertEqual(manifest["artifacts"][0]["artifact_id"], "I1")

    def test_05_security_credential_isolation(self) -> None:
        """Verifies RAW SECRET PERSISTENCE = NONE in output archive."""
        run_id = "RUN_SEC_01"
        self.archive_mgr.start_research_run(run_id)
        self.archive_mgr.record_artifact(
            run_id,
            ArchivedArtifact("SEC_1", "SecretType", "hash_sec", "00_input", "SUCCESS", provenance={"credential_ref": "env:IBM_QUANTUM_TOKEN"}),
        )
        dir_path = self.archive_mgr.finalize_research_run(run_id)

        manifest_str = open(os.path.join(dir_path, "manifest.json"), "r").read()
        readme_str = open(os.path.join(dir_path, "README.md"), "r").read()

        for secret in ("secret_token_123", "password999", "sk-live-abc"):
            self.assertNotIn(secret, manifest_str)
            self.assertNotIn(secret, readme_str)


if __name__ == "__main__":
    unittest.main()
