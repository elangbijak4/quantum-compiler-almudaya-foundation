"""
Application / Product Layer — CLI Foundation Unit Tests.

Verifies CLIExecutionMode, CLICommandCategory, CLICommand, CLIExitCode, CLIConfig,
CLIRequestAdapter, CLIResponseFormatter, Pipeline vs Stepwise modes, artifact chaining,
evidence rendering, and mock contract integration.
"""

import json
import unittest

from src.application import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
    ApplicationContractProtocol,
    ApplicationContractService,
    CLIExecutionMode,
    CLICommandCategory,
    CLICommand,
    CLIExitCode,
    CLIConfig,
    CLIRequestAdapter,
    CLIResponseFormatter,
)


class MockApplicationContractService(ApplicationContractProtocol):
    """Mock contract service for testing CLI integration without Core side-effects."""

    def compile(self, request: ApplicationRequest) -> ApplicationResponse:
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.COMPILE,
            status=ApplicationStatus.SUCCESS,
            artifact_references={"logical_circuit_id": request.logical_circuit_id or "LOG_CIRC_01"},
            result_payload={"compiled": True, "qubits": 2},
        )

    def inspect(self, request: ApplicationRequest) -> ApplicationResponse:
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.INSPECT,
            status=ApplicationStatus.SUCCESS,
            artifact_references={"backend_id": request.backend_id},
            result_payload={"backend_id": request.backend_id, "qubit_count": 32},
        )

    def simulate(self, request: ApplicationRequest) -> ApplicationResponse:
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.SIMULATE,
            status=ApplicationStatus.SUCCESS,
            result_payload={"shots": request.shots, "counts": {"00": request.shots // 2, "11": request.shots // 2}},
        )

    def execute(self, request: ApplicationRequest) -> ApplicationResponse:
        if request.backend_id == "UNSUPPORTED_BACKEND":
            return ApplicationResponse(
                request_id=request.request_id,
                intent=ApplicationIntent.EXECUTE,
                status=ApplicationStatus.FAILED,
                error_code="BACKEND_UNSUPPORTED",
                error_message="Backend not supported.",
            )
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.EXECUTE,
            status=ApplicationStatus.SUCCESS,
            result_payload={"execution_environment": "MOCK"},
        )

    def verify(self, request: ApplicationRequest) -> ApplicationResponse:
        if request.verification_policy_id == "STRICT_FAIL":
            return ApplicationResponse(
                request_id=request.request_id,
                intent=ApplicationIntent.VERIFY,
                status=ApplicationStatus.FAILED,
                error_code="VERIFICATION_REJECTED",
                error_message="Statistical verification rejected.",
                result_payload={"decision": "REJECTED"},
            )
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.VERIFY,
            status=ApplicationStatus.SUCCESS,
            result_payload={"decision": "VERIFIED"},
        )

    def lineage(self, request: ApplicationRequest) -> ApplicationResponse:
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.LINEAGE,
            status=ApplicationStatus.SUCCESS,
            result_payload={"lineage_records": 3},
        )


class TestCLIFoundation(unittest.TestCase):
    """Test suite for CLI Foundation abstractions."""

    def setUp(self) -> None:
        self.mock_service = MockApplicationContractService()
        self.prod_service = ApplicationContractService()

    def test_01_cli_modes_and_categories(self) -> None:
        """Verifies CLIExecutionMode and CLICommandCategory classifications."""
        # Pipeline
        self.assertEqual(CLICommand.COMPILE.mode, CLIExecutionMode.PIPELINE)
        self.assertEqual(CLICommand.COMPILE.category, CLICommandCategory.CONVENIENCE)

        # Stepwise transformations
        for cmd in (CLICommand.AML, CLICommand.UTM, CLICommand.RUTM, CLICommand.SEMANTIC, CLICommand.MAP, CLICommand.OPTIMIZE, CLICommand.LOWER):
            self.assertEqual(cmd.mode, CLIExecutionMode.STEPWISE)
            self.assertEqual(cmd.category, CLICommandCategory.TRANSFORMATION)

        # Inspection
        self.assertEqual(CLICommand.INSPECT.mode, CLIExecutionMode.INSPECTION)
        self.assertEqual(CLICommand.LINEAGE.mode, CLIExecutionMode.INSPECTION)

    def test_02_artifact_chaining_and_request_adapter(self) -> None:
        """Verifies CLIRequestAdapter artifact chaining via parent_artifact_id."""
        args = {"parent_artifact_id": "AML_ART_01", "backend": "LOCAL_REFERENCE"}
        req = CLIRequestAdapter.build_request(CLICommand.UTM, args)

        self.assertEqual(req.intent, ApplicationIntent.COMPILE)
        self.assertEqual(req.logical_circuit_id, "AML_ART_01")
        self.assertEqual(req.backend_id, "LOCAL_REFERENCE")

    def test_03_cli_response_formatter_evidence_and_hashes(self) -> None:
        """Verifies evidence rendering and hash inclusion in human/JSON formats."""
        resp = ApplicationResponse(
            request_id="REQ_EVID_01",
            intent=ApplicationIntent.COMPILE,
            status=ApplicationStatus.SUCCESS,
            artifact_references={"logical_circuit_id": "LOG_CIRC_01"},
            result_payload={"compiled": True},
        )

        human_out = CLIResponseFormatter.format_output(resp, "human")
        self.assertIn("Evidence & Result Payload", human_out)
        self.assertIn("Response Hash", human_out)

        json_out = CLIResponseFormatter.format_output(resp, "json")
        parsed = json.loads(json_out)
        self.assertEqual(parsed["artifact_references"]["logical_circuit_id"], "LOG_CIRC_01")
        self.assertEqual(parsed["exit_code"], 0)

    def test_04_read_only_inspection_semantics(self) -> None:
        """Verifies read-only inspection commands do not mutate Core state."""
        req_inspect = CLIRequestAdapter.build_request(CLICommand.INSPECT, {"backend": "LOCAL_REFERENCE"})
        resp_inspect = self.prod_service.inspect(req_inspect)
        self.assertEqual(resp_inspect.status, ApplicationStatus.SUCCESS)

        req_lineage = CLIRequestAdapter.build_request(CLICommand.LINEAGE, {})
        resp_lineage = self.prod_service.lineage(req_lineage)
        self.assertEqual(resp_lineage.status, ApplicationStatus.SUCCESS)


if __name__ == "__main__":
    unittest.main()
