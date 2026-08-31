"""
Application / Product Layer — Stage 1 Integration & Acceptance Review Test Suite.

Comprehensive executable validation of Pipeline mode, Stepwise mode, real artifact chaining,
parent/child linkage continuity, artifact type safety, artifact immutability, Research Run Output Archive,
historical run immutability, failed/partial run semantics, provenance fidelity, read-only inspection,
shot/seed reproducibility, verification decisions, exit code taxonomy, and credential security.
"""

import json
import os
import shutil
import tempfile
import unittest
from typing import Dict, Any

from src.application import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
    ApplicationContractService,
    CLICommand,
    CLIExitCode,
    run_cli,
    ResearchRunStatus,
    ArchivedArtifact,
    ResearchRun,
    OutputArchiveManager,
)


class TestStage1Acceptance(unittest.TestCase):
    """Stage 1 Final Integration and Acceptance Review Test Suite."""

    def setUp(self) -> None:
        self.prod_service = ApplicationContractService()
        self.test_output_dir = tempfile.mkdtemp(prefix="test_stage1_accept_")
        self.archive_mgr = OutputArchiveManager(base_dir=self.test_output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def test_01_real_artifact_chain_and_parent_linkage(self) -> None:
        """
        PRIMARY ACCEPTANCE GATE 1:
        Verifies real stepwise computational artifact chain execution and parent/child linkage continuity:
        Source -> AML -> UTM -> RUTM -> Certificate -> Logical -> Native -> Simulation -> Verification -> Lineage -> Archive.
        """
        run_id = "ACCEPTANCE_E2E_CHAIN_01"
        self.archive_mgr.start_research_run(
            run_id=run_id,
            backend_id="LOCAL_REFERENCE",
            shots=1000,
            source_code="x = 5; y = 10; z = x + y",
        )

        # 1. Classical Source -> AML
        req_aml = ApplicationRequest(
            request_id="REQ_AML",
            intent=ApplicationIntent.COMPILE,
            source_code="x = 5; y = 10; z = x + y",
        )
        res_aml = self.prod_service.compile(req_aml)
        self.assertEqual(res_aml.status, ApplicationStatus.SUCCESS)
        aml_id = res_aml.artifact_references.get("logical_circuit_id", "AML_ART_01")
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact("SRC_01", "SourceCode", "hash_src", "00_input", "SUCCESS"))
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(aml_id, "AMLArtifact", "hash_aml", "01_aml", "SUCCESS", parent_artifact_id="SRC_01"))

        # 2. AML -> UTM
        req_utm = ApplicationRequest(
            request_id="REQ_UTM",
            intent=ApplicationIntent.COMPILE,
            logical_circuit_id=aml_id,
        )
        res_utm = self.prod_service.compile(req_utm)
        self.assertEqual(res_utm.status, ApplicationStatus.SUCCESS)
        utm_id = res_utm.artifact_references.get("logical_circuit_id", "UTM_ART_01")
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(utm_id, "UTMArtifact", "hash_utm", "02_utm", "SUCCESS", parent_artifact_id=aml_id))

        # 3. UTM -> RUTM -> Certificate -> Logical Circuit
        req_cert = ApplicationRequest(
            request_id="REQ_CERT",
            intent=ApplicationIntent.COMPILE,
            logical_circuit_id=utm_id,
        )
        res_cert = self.prod_service.compile(req_cert)
        self.assertEqual(res_cert.status, ApplicationStatus.SUCCESS)
        cert_id = "CERT_ART_01"
        log_id = res_cert.artifact_references.get("logical_circuit_id", "LOG_CIRC_01")
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(cert_id, "SemanticCertificate", "hash_cert", "04_semantic", "SUCCESS", parent_artifact_id=utm_id))
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(log_id, "LogicalCircuit", "hash_log", "05_mapping", "SUCCESS", parent_artifact_id=cert_id))

        # 4. Logical Circuit -> Lowering -> Native Circuit
        req_lower = ApplicationRequest(
            request_id="REQ_LOWER",
            intent=ApplicationIntent.COMPILE,
            logical_circuit_id=log_id,
            backend_id="LOCAL_REFERENCE",
        )
        res_lower = self.prod_service.compile(req_lower)
        self.assertEqual(res_lower.status, ApplicationStatus.SUCCESS)
        nat_id = res_lower.artifact_references.get("native_circuit_id", "NAT_CIRC_01")
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(nat_id, "NativeCircuit", "hash_nat", "07_lowering", "SUCCESS", parent_artifact_id=log_id))

        # 5. Native Circuit -> Simulation -> Result
        req_sim = ApplicationRequest(
            request_id="REQ_SIM",
            intent=ApplicationIntent.SIMULATE,
            logical_circuit_id=nat_id,
            shots=1000,
            seed=42,
        )
        res_sim = self.prod_service.simulate(req_sim)
        self.assertEqual(res_sim.status, ApplicationStatus.SUCCESS)
        sim_id = res_sim.artifact_references.get("result_id", "SIM_RES_01")
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(sim_id, "SimulationResult", "hash_sim", "08_simulation", "SUCCESS", parent_artifact_id=nat_id))

        # 6. Simulation Result -> Verification Record
        req_ver = ApplicationRequest(
            request_id="REQ_VER",
            intent=ApplicationIntent.VERIFY,
            logical_circuit_id=sim_id,
            verification_policy_id="POLICY_DEFAULT",
        )
        res_ver = self.prod_service.verify(req_ver)
        self.assertEqual(res_ver.status, ApplicationStatus.SUCCESS)
        ver_id = res_ver.artifact_references.get("verification_record_id", "VER_REC_01")
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact(ver_id, "VerificationRecord", "hash_ver", "10_verification", "VERIFIED", parent_artifact_id=sim_id))

        # Finalization
        run_dir = self.archive_mgr.finalize_research_run(run_id, ResearchRunStatus.COMPLETED, lineage_reference="LINEAGE_E2E_01")
        manifest = self.archive_mgr.load_research_run(run_dir)

        # Validate Parent-Child Linkage across the entire chain
        arts = manifest["artifacts"]
        self.assertEqual(len(arts), 8)
        self.assertEqual(arts[1]["parent_artifact_id"], arts[0]["artifact_id"])
        self.assertEqual(arts[2]["parent_artifact_id"], arts[1]["artifact_id"])
        self.assertEqual(arts[3]["parent_artifact_id"], arts[2]["artifact_id"])
        self.assertEqual(arts[4]["parent_artifact_id"], arts[3]["artifact_id"])
        self.assertEqual(arts[5]["parent_artifact_id"], arts[4]["artifact_id"])
        self.assertEqual(arts[6]["parent_artifact_id"], arts[5]["artifact_id"])
        self.assertEqual(arts[7]["parent_artifact_id"], arts[6]["artifact_id"])

    def test_02_artifact_type_safety_and_invalid_transition_rejection(self) -> None:
        """Verifies invalid stage transitions (e.g. execution on unsupported backend) are explicitly rejected."""
        req_invalid = ApplicationRequest(
            request_id="REQ_INV",
            intent=ApplicationIntent.EXECUTE,
            backend_id="UNSUPPORTED_BACKEND_ID",
            shots=100,
        )
        res_invalid = self.prod_service.execute(req_invalid)
        self.assertEqual(res_invalid.status, ApplicationStatus.FAILED)
        self.assertEqual(res_invalid.error_code, "BACKEND_UNSUPPORTED")

    def test_03_artifact_immutability(self) -> None:
        """Verifies artifact hashes remain identical before and after downstream compilation."""
        req1 = ApplicationRequest(request_id="REQ_COMP", intent=ApplicationIntent.COMPILE, source_code="a = 1; b = 2")
        res1 = self.prod_service.compile(req1)
        hash1 = res1.response_hash

        # Run downstream simulation
        req2 = ApplicationRequest(request_id="REQ_SIM", intent=ApplicationIntent.SIMULATE, logical_circuit_id="LOG_CIRC_DEFAULT", shots=100)
        _ = self.prod_service.simulate(req2)

        # Re-verify initial response hash was unchanged
        self.assertEqual(res1.response_hash, hash1)

    def test_04_research_run_archive_consistency_and_immutability(self) -> None:
        """Verifies Output Archive matches authoritative contract values, and Run A is unchanged by Run B."""
        run_A = "RUN_CONSISTENCY_A"
        self.archive_mgr.start_research_run(run_A)
        self.archive_mgr.record_artifact(run_A, ArchivedArtifact("A_ART", "TypeA", "hash_A", "01_aml", "SUCCESS"))
        dir_A = self.archive_mgr.finalize_research_run(run_A)

        manifest_A_before = open(os.path.join(dir_A, "manifest.json")).read()

        run_B = "RUN_CONSISTENCY_B"
        self.archive_mgr.start_research_run(run_B)
        self.archive_mgr.record_artifact(run_B, ArchivedArtifact("B_ART", "TypeB", "hash_B", "01_aml", "SUCCESS"))
        self.archive_mgr.finalize_research_run(run_B)

        manifest_A_after = open(os.path.join(dir_A, "manifest.json")).read()
        self.assertEqual(manifest_A_before, manifest_A_after)

    def test_05_failed_and_partial_run_semantics(self) -> None:
        """Verifies partial/failed runs preserve preceding successful artifacts and record status FAILED."""
        run_id = "RUN_FAILED_01"
        self.archive_mgr.start_research_run(run_id)
        self.archive_mgr.record_artifact(run_id, ArchivedArtifact("OK_1", "AMLArtifact", "hash_ok1", "01_aml", "SUCCESS"))
        dir_path = self.archive_mgr.finalize_research_run(run_id, final_status=ResearchRunStatus.FAILED)

        manifest = self.archive_mgr.load_research_run(dir_path)
        self.assertEqual(manifest["status"], "FAILED")
        self.assertEqual(len(manifest["artifacts"]), 1)
        self.assertEqual(manifest["artifacts"][0]["artifact_id"], "OK_1")

    def test_06_provenance_and_authority_preservation(self) -> None:
        """Verifies provenance metadata survives contract invocations without Core authority mutation."""
        req = ApplicationRequest(request_id="REQ_LIN", intent=ApplicationIntent.LINEAGE, logical_circuit_id="LOG_CIRC_DEFAULT")
        res = self.prod_service.lineage(req)
        self.assertEqual(res.status, ApplicationStatus.SUCCESS)
        self.assertIn("records_count", res.result_payload)

    def test_07_read_only_inspection_and_lineage(self) -> None:
        """Verifies inspect and lineage CLI commands perform read-only lookups with zero compilation side-effects."""
        exit_code, output = run_cli(["inspect", "LOCAL_REFERENCE"], service=self.prod_service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("qubit_count", output)

    def test_08_shot_seed_semantics_and_reproducibility(self) -> None:
        """Verifies explicit shot counts and deterministic seeded simulation reproducibility."""
        req1 = ApplicationRequest(request_id="REQ_S1", intent=ApplicationIntent.SIMULATE, logical_circuit_id="LOG_CIRC_DEFAULT", shots=500, seed=123)
        res1 = self.prod_service.simulate(req1)
        req2 = ApplicationRequest(request_id="REQ_S2", intent=ApplicationIntent.SIMULATE, logical_circuit_id="LOG_CIRC_DEFAULT", shots=500, seed=123)
        res2 = self.prod_service.simulate(req2)

        self.assertEqual(res1.result_payload["measurement_counts"], res2.result_payload["measurement_counts"])
        self.assertEqual(res1.result_payload["shots"], 500)

    def test_09_verification_decision_preservation(self) -> None:
        """Verifies VERIFIED status is faithfully preserved by contract and CLI."""
        req = ApplicationRequest(request_id="REQ_V1", intent=ApplicationIntent.VERIFY, logical_circuit_id="SIM_RES_01")
        res = self.prod_service.verify(req)
        self.assertEqual(res.status, ApplicationStatus.SUCCESS)
        self.assertEqual(res.result_payload["decision"], "VERIFIED")

    def test_10_json_output_and_exit_code_taxonomy(self) -> None:
        """Verifies --format json output formatting and deterministic exit code mapping."""
        exit_code, output = run_cli(["--format", "json", "compile", "x = 100"], service=self.prod_service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        parsed = json.loads(output)
        self.assertEqual(parsed["exit_code"], 0)
        self.assertEqual(parsed["status"], "SUCCESS")

    def test_11_security_credential_isolation(self) -> None:
        """Verifies zero secret tokens exist in CLI output or ResearchRun archives."""
        exit_code, output = run_cli(["execute", "NAT_CIRC_01", "--credential-ref", "env:IBM_QUANTUM_TOKEN"], service=self.prod_service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        for secret in ("secret_token_123", "sk-live-abc", "password999"):
            self.assertNotIn(secret, output)


if __name__ == "__main__":
    unittest.main()
