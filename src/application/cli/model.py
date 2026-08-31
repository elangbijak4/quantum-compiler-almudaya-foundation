"""
Application / Product Layer — CLI Foundation Models.

Provides CLIExecutionMode, CLICommandCategory, CLICommand, CLIExitCode, CLIConfig,
CLIRequestAdapter, and CLIResponseFormatter supporting Pipeline and Stepwise Inspection modes.
"""

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Dict, Any, Optional

from src.application.model import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
)


class CLIExecutionMode(str, Enum):
    """CLI Execution Modes."""

    PIPELINE = "pipeline"
    STEPWISE = "stepwise"
    INSPECTION = "inspection"


class CLICommandCategory(str, Enum):
    """CLI Command Categories."""

    TRANSFORMATION = "transformation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    INSPECTION = "inspection"
    CONVENIENCE = "convenience"


class CLICommand(str, Enum):
    """Supported CLI Commands covering Pipeline and Stepwise Modes."""

    # Convenience Pipeline Mode
    COMPILE = "compile"

    # Stepwise Transformation Commands
    AML = "aml"
    UTM = "utm"
    RUTM = "rutm"
    SEMANTIC = "semantic"
    MAP = "map"
    OPTIMIZE = "optimize"
    LOWER = "lower"

    # Execution Commands
    SIMULATE = "simulate"
    EXECUTE = "execute"

    # Validation Commands
    VERIFY = "verify"

    # Read-Only Inspection Commands
    INSPECT = "inspect"
    LINEAGE = "lineage"

    @property
    def mode(self) -> CLIExecutionMode:
        if self == CLICommand.COMPILE:
            return CLIExecutionMode.PIPELINE
        if self in (CLICommand.INSPECT, CLICommand.LINEAGE):
            return CLIExecutionMode.INSPECTION
        return CLIExecutionMode.STEPWISE

    @property
    def category(self) -> CLICommandCategory:
        if self == CLICommand.COMPILE:
            return CLICommandCategory.CONVENIENCE
        if self in (CLICommand.SIMULATE, CLICommand.EXECUTE):
            return CLICommandCategory.EXECUTION
        if self == CLICommand.VERIFY:
            return CLICommandCategory.VALIDATION
        if self in (CLICommand.INSPECT, CLICommand.LINEAGE):
            return CLICommandCategory.INSPECTION
        return CLICommandCategory.TRANSFORMATION


class CLIExitCode(int, Enum):
    """Deterministic CLI Exit Code Taxonomy."""

    SUCCESS = 0
    INVALID_USER_INPUT = 1
    COMPUTATIONAL_FAILURE = 2
    EXECUTION_FAILURE = 3
    VERIFICATION_REJECTED = 4
    VERIFICATION_INCONCLUSIVE = 5
    INTERNAL_ERROR = 99


@dataclass(frozen=True)
class CLIConfig:
    """CLI User/Project Configuration Data Model."""

    default_backend: str = "LOCAL_REFERENCE"
    default_shots: int = 1000
    output_format: str = "human"  # "human" or "json"
    seed_preference: Optional[int] = None
    credential_ref: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Returns non-sensitive dictionary representation."""
        return {
            "default_backend": self.default_backend,
            "default_shots": self.default_shots,
            "output_format": self.output_format,
            "seed_preference": self.seed_preference,
            "credential_ref": self.credential_ref,
        }


class CLIRequestAdapter:
    """Adapts CLI pipeline or stepwise commands into an immutable ApplicationRequest."""

    @staticmethod
    def build_request(
        command: CLICommand,
        args: Dict[str, Any],
        config: Optional[CLIConfig] = None,
    ) -> ApplicationRequest:
        """Constructs ApplicationRequest enforcing configuration precedence and artifact chaining."""
        cfg = config or CLIConfig()

        intent_map = {
            CLICommand.COMPILE: ApplicationIntent.COMPILE,
            CLICommand.AML: ApplicationIntent.COMPILE,
            CLICommand.UTM: ApplicationIntent.COMPILE,
            CLICommand.RUTM: ApplicationIntent.COMPILE,
            CLICommand.SEMANTIC: ApplicationIntent.COMPILE,
            CLICommand.MAP: ApplicationIntent.COMPILE,
            CLICommand.OPTIMIZE: ApplicationIntent.COMPILE,
            CLICommand.LOWER: ApplicationIntent.COMPILE,
            CLICommand.SIMULATE: ApplicationIntent.SIMULATE,
            CLICommand.EXECUTE: ApplicationIntent.EXECUTE,
            CLICommand.VERIFY: ApplicationIntent.VERIFY,
            CLICommand.INSPECT: ApplicationIntent.INSPECT,
            CLICommand.LINEAGE: ApplicationIntent.LINEAGE,
        }

        # Precedence: Explicit Arg > Configuration > Default Policy
        backend_id = args.get("backend") or cfg.default_backend
        shots = args.get("shots") if args.get("shots") is not None else cfg.default_shots
        seed = args.get("seed") if args.get("seed") is not None else cfg.seed_preference
        credential_ref = args.get("credential_ref") or cfg.credential_ref

        req_id = args.get("request_id") or f"REQ_CLI_{command.value.upper()}"

        return ApplicationRequest(
            request_id=req_id,
            intent=intent_map[command],
            source_code=args.get("source_code"),
            logical_circuit_id=args.get("logical_circuit_id") or args.get("parent_artifact_id"),
            native_circuit_id=args.get("native_circuit_id"),
            backend_id=backend_id,
            provider_id=args.get("provider", backend_id),
            shots=shots,
            seed=seed,
            credential_ref=credential_ref,
            verification_policy_id=args.get("verification_policy_id", "POLICY_DEFAULT"),
        )


class CLIResponseFormatter:
    """Formats ApplicationResponse into CLI output, evidence rendering, and exit codes."""

    @staticmethod
    def determine_exit_code(response: ApplicationResponse) -> CLIExitCode:
        """Maps ApplicationResponse status and errors to CLIExitCode."""
        if response.status == ApplicationStatus.SUCCESS:
            return CLIExitCode.SUCCESS

        if response.status == ApplicationStatus.INCONCLUSIVE:
            return CLIExitCode.VERIFICATION_INCONCLUSIVE

        # Failure classifications
        error_code = response.error_code or ""
        if "REJECTED" in error_code or response.result_payload.get("decision") == "REJECTED":
            return CLIExitCode.VERIFICATION_REJECTED

        if any(kw in error_code for kw in ("INPUT", "INVALID", "ARGUMENT")):
            return CLIExitCode.INVALID_USER_INPUT

        if any(kw in error_code for kw in ("EXECUTION", "SUBMISSION", "PROVIDER", "BACKEND")):
            return CLIExitCode.EXECUTION_FAILURE

        if any(kw in error_code for kw in ("COMPUTATION", "MAPPING", "LOWERING", "COMPILATION")):
            return CLIExitCode.COMPUTATIONAL_FAILURE

        return CLIExitCode.INTERNAL_ERROR

    @staticmethod
    def format_output(response: ApplicationResponse, output_format: str = "human") -> str:
        """Renders human-readable text or machine-readable JSON preserving evidence & provenance."""
        exit_code = CLIResponseFormatter.determine_exit_code(response)

        if output_format == "json":
            payload = {
                "request_id": response.request_id,
                "intent": response.intent.value,
                "status": response.status.value,
                "exit_code": exit_code.value,
                "error_code": response.error_code,
                "error_message": response.error_message,
                "artifact_references": response.artifact_references,
                "result_payload": response.result_payload,
                "diagnostics": response.diagnostics,
                "response_hash": response.response_hash,
            }
            return json.dumps(payload, indent=2)

        # Human-readable evidence & provenance rendering
        lines = [
            f"=== Quantum Compiler CLI [{response.intent.value.upper()}] ===",
            f"Operation    : {response.intent.value}",
            f"Status       : {response.status.value}",
            f"Exit Code    : {exit_code.value} ({exit_code.name})",
            f"Request ID   : {response.request_id}",
            f"Response Hash: {response.response_hash[:16]}...",
        ]

        if response.error_code:
            lines.append(f"Error Code   : {response.error_code}")
        if response.error_message:
            lines.append(f"Error Msg    : {response.error_message}")

        if response.artifact_references:
            lines.append("--- Artifact References ---")
            for k, v in response.artifact_references.items():
                lines.append(f"  {k}: {v}")

        if response.result_payload:
            lines.append("--- Evidence & Result Payload ---")
            for k, v in response.result_payload.items():
                lines.append(f"  {k}: {v}")

        return "\n".join(lines)
