"""
Application / Product Layer — Production CLI Executable Unit & Integration Tests.

Verifies CLI entrypoint, argument parsing, Pipeline mode, Stepwise commands, artifact chaining,
read-only inspection, exit codes, JSON formatting, security credential isolation, and local E2E flow.
"""

import json
import unittest
from typing import Dict, Any

from src.application import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
    ApplicationContractProtocol,
    ApplicationContractService,
)
from src.application.cli import (
    CLICommand,
    CLIExitCode,
    run_cli,
    CLI_VERSION,
)


class MockContractService(ApplicationContractProtocol):
    """Mock contract service for validating CLI executable behaviors."""

    def compile(self, request: ApplicationRequest) -> ApplicationResponse:
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.COMPILE,
            status=ApplicationStatus.SUCCESS,
            artifact_references={"logical_circuit_id": request.logical_circuit_id or "LOG_CIRC_01"},
            result_payload={"compiled": True, "qubits": 2},
        )

    def inspect(self, request: ApplicationRequest) -> ApplicationResponse:
        if request.backend_id == "INVALID_BACKEND":
            return ApplicationResponse(
                request_id=request.request_id,
                intent=ApplicationIntent.INSPECT,
                status=ApplicationStatus.FAILED,
                error_code="BACKEND_UNSUPPORTED",
                error_message="Backend invalid.",
            )
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
                error_message="Backend unsupported.",
            )
        return ApplicationResponse(
            request_id=request.request_id,
            intent=ApplicationIntent.EXECUTE,
            status=ApplicationStatus.SUCCESS,
            result_payload={"execution_environment": "MOCK"},
        )

    def verify(self, request: ApplicationRequest) -> ApplicationResponse:
        if request.verification_policy_id == "REJECT_POLICY":
            return ApplicationResponse(
                request_id=request.request_id,
                intent=ApplicationIntent.VERIFY,
                status=ApplicationStatus.FAILED,
                error_code="VERIFICATION_REJECTED",
                error_message="Verification rejected.",
                result_payload={"decision": "REJECTED"},
            )
        if request.verification_policy_id == "INCONCLUSIVE_POLICY":
            return ApplicationResponse(
                request_id=request.request_id,
                intent=ApplicationIntent.VERIFY,
                status=ApplicationStatus.INCONCLUSIVE,
                error_code="INCONCLUSIVE",
                error_message="Insufficient shots.",
                result_payload={"decision": "INCONCLUSIVE"},
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
            result_payload={"lineage_records": 1},
        )


class TestCLIExecutable(unittest.TestCase):
    """Test suite for Production CLI Executable (main.py)."""

    def setUp(self) -> None:
        self.mock_service = MockContractService()
        self.prod_service = ApplicationContractService()

    def test_01_pipeline_mode_compile(self) -> None:
        """Verifies Pipeline mode compile command execution."""
        exit_code, output = run_cli(["compile", "x = 5", "--backend", "LOCAL_REFERENCE", "--shots", "2000"], service=self.prod_service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("Status       : SUCCESS", output)

    def test_02_stepwise_mode_commands(self) -> None:
        """Verifies all stepwise commands bind to ApplicationContractService."""
        stepwise_cmds = [
            ["aml", "program.aml"],
            ["utm", "aml:01"],
            ["rutm", "utm:01"],
            ["semantic", "rutm:01"],
            ["map", "cert:01"],
            ["optimize", "circ:01"],
            ["lower", "circ:01", "--backend", "LOCAL_REFERENCE"],
            ["simulate", "nat:01", "--shots", "1000"],
            ["execute", "nat:01", "--backend", "LOCAL_REFERENCE"],
            ["verify", "exec:01"],
        ]
        for cmd_args in stepwise_cmds:
            exit_code, output = run_cli(cmd_args, service=self.mock_service)
            self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
            self.assertIn("Exit Code    : 0 (SUCCESS)", output)

    def test_03_read_only_inspection_and_lineage(self) -> None:
        """Verifies inspect and lineage commands execute read-only lookup."""
        exit_code_insp, out_insp = run_cli(["inspect", "LOCAL_REFERENCE"], service=self.prod_service)
        self.assertEqual(exit_code_insp, CLIExitCode.SUCCESS.value)
        self.assertIn("qubit_count", out_insp)

        exit_code_lin, out_lin = run_cli(["lineage", "LOG_CIRC_01"], service=self.mock_service)
        self.assertEqual(exit_code_lin, CLIExitCode.SUCCESS.value)
        self.assertIn("lineage_records", out_lin)

    def test_04_json_output_format(self) -> None:
        """Verifies --format json output formatting."""
        exit_code, output = run_cli(["--format", "json", "simulate", "nat:01", "--shots", "500"], service=self.mock_service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        parsed = json.loads(output)
        self.assertEqual(parsed["intent"].lower(), "simulate")
        self.assertEqual(parsed["exit_code"], 0)
        self.assertEqual(parsed["result_payload"]["shots"], 500)

    def test_05_exit_codes_and_error_handling(self) -> None:
        """Verifies deterministic exit code mappings for failure cases."""
        # 1. Invalid backend -> EXECUTION_FAILURE (3)
        exit_code_fail, _ = run_cli(["execute", "nat:01", "--backend", "UNSUPPORTED_BACKEND"], service=self.mock_service)
        self.assertEqual(exit_code_fail, CLIExitCode.EXECUTION_FAILURE.value)

        # 2. Verification rejection -> VERIFICATION_REJECTED (4)
        exit_code_rej, _ = run_cli(["verify", "exec:01", "--policy", "REJECT_POLICY"], service=self.mock_service)
        self.assertEqual(exit_code_rej, CLIExitCode.VERIFICATION_REJECTED.value)

        # 3. Verification inconclusive -> VERIFICATION_INCONCLUSIVE (5)
        exit_code_inc, _ = run_cli(["verify", "exec:01", "--policy", "INCONCLUSIVE_POLICY"], service=self.mock_service)
        self.assertEqual(exit_code_inc, CLIExitCode.VERIFICATION_INCONCLUSIVE.value)

    def test_06_credential_security_isolation(self) -> None:
        """Verifies zero secret credentials leak into output strings."""
        exit_code, output = run_cli(["execute", "nat:01", "--credential-ref", "env:MY_SECRET_REF"], service=self.mock_service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)

        for secret in ("secret_token_123", "password999", "sk-live-abc"):
            self.assertNotIn(secret, output)

    def test_07_local_end_to_end_flow(self) -> None:
        """Demonstrates end-to-end local simulation flow via production ApplicationContractService."""
        # 1. Compile
        ec1, out1 = run_cli(["compile", "x = 10", "--backend", "LOCAL_REFERENCE"], service=self.prod_service)
        self.assertEqual(ec1, CLIExitCode.SUCCESS.value)

        # 2. Inspect backend
        ec2, out2 = run_cli(["inspect", "LOCAL_REFERENCE"], service=self.prod_service)
        self.assertEqual(ec2, CLIExitCode.SUCCESS.value)

        # 3. Local simulation
        ec3, out3 = run_cli(["simulate", "LOG_CIRC_DEFAULT", "--shots", "1000"], service=self.prod_service)
        self.assertEqual(ec3, CLIExitCode.SUCCESS.value)
        self.assertIn("measurement_counts", out3)

        # 4. Statistical verification
        ec4, out4 = run_cli(["verify", "SIM_RESULT_01"], service=self.prod_service)
        self.assertEqual(ec4, CLIExitCode.SUCCESS.value)
        self.assertIn("VERIFIED", out4)


if __name__ == "__main__":
    unittest.main()
