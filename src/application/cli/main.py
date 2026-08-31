"""
Application / Product Layer — Production CLI Executable Entrypoint.

Provides the main CLI entrypoint for Quantum Compiler, parsing command line arguments,
binding requests to ApplicationContractService, rendering evidence/output, and returning
deterministic exit codes.
"""

import argparse
import json
import sys
from typing import List, Optional, Tuple, Any

from src.application.contract import ApplicationContractProtocol
from src.application.service import ApplicationContractService
from src.application.cli.model import (
    CLICommand,
    CLIExitCode,
    CLIConfig,
    CLIRequestAdapter,
    CLIResponseFormatter,
)

CLI_VERSION = "1.0.0"


def create_cli_parser() -> argparse.ArgumentParser:
    """Constructs the production argparse command tree for quantum-compiler."""
    parser = argparse.ArgumentParser(
        prog="quantum-compiler",
        description="Quantum Compiler Production CLI — Proof-Oriented Quantum Compiler Pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"quantum-compiler v{CLI_VERSION}",
        help="Show compiler version and exit.",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Specify output format (default: human).",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom CLI configuration file.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available compiler commands")

    # 1. Pipeline Convenience Command
    compile_parser = subparsers.add_parser("compile", help="Run full compilation pipeline on classical input.")
    compile_parser.add_argument("input", help="Classical source program file or inline code.")
    compile_parser.add_argument("--backend", type=str, default="LOCAL_REFERENCE", help="Target backend identifier.")
    compile_parser.add_argument("--shots", type=int, default=1000, help="Shot count for simulation/execution.")
    compile_parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic sampling.")

    # 2. Stepwise Transformation Commands
    aml_parser = subparsers.add_parser("aml", help="Transform classical program into Abstract Machine Language (Module 1).")
    aml_parser.add_argument("input", help="Classical program file path or code.")

    utm_parser = subparsers.add_parser("utm", help="Transform AML artifact to Universal Turing Machine IR (Module 2).")
    utm_parser.add_argument("artifact", help="Input AML artifact ID or path.")

    rutm_parser = subparsers.add_parser("rutm", help="Transform UTM IR to Reversible UTM IR (Module 3).")
    rutm_parser.add_argument("artifact", help="Input UTM artifact ID.")

    semantic_parser = subparsers.add_parser("semantic", help="Synthesize reversible gates and issue Semantic Certificate (Module 4).")
    semantic_parser.add_argument("artifact", help="Input RUTM artifact ID.")

    map_parser = subparsers.add_parser("map", help="Physicalize logical circuit to backend topology (Module 5).")
    map_parser.add_argument("artifact", help="Input logical circuit artifact ID or certificate ID.")

    optimize_parser = subparsers.add_parser("optimize", help="Apply Pareto optimization rewrite rules (Module 6).")
    optimize_parser.add_argument("artifact", help="Input circuit artifact ID.")

    lower_parser = subparsers.add_parser("lower", help="Lower logical circuit to native gate set (Module 7 Stage 2).")
    lower_parser.add_argument("artifact", help="Input logical circuit artifact ID.")
    lower_parser.add_argument("--backend", type=str, default="LOCAL_REFERENCE", help="Target backend identifier.")

    # 3. Execution Commands
    sim_parser = subparsers.add_parser("simulate", help="Run local reference simulation (Module 7 Stage 3).")
    sim_parser.add_argument("artifact", help="Input native or logical circuit artifact ID.")
    sim_parser.add_argument("--shots", type=int, default=1000, help="Shot count for simulation.")
    sim_parser.add_argument("--seed", type=int, default=None, help="Random seed for simulation.")

    exec_parser = subparsers.add_parser("execute", help="Submit execution job to provider adapter (Module 7 Stage 4).")
    exec_parser.add_argument("artifact", help="Input native circuit artifact ID.")
    exec_parser.add_argument("--backend", type=str, default="LOCAL_REFERENCE", help="Target backend identifier.")
    exec_parser.add_argument("--provider", type=str, default=None, help="Provider identifier (defaults to backend).")
    exec_parser.add_argument("--shots", type=int, default=1000, help="Execution shot count.")
    exec_parser.add_argument("--credential-ref", type=str, default=None, help="Non-sensitive credential reference.")

    # 4. Validation Commands
    verify_parser = subparsers.add_parser("verify", help="Request statistical verification (Module 7 Stage 5).")
    verify_parser.add_argument("artifact", help="Input execution or result artifact ID.")
    verify_parser.add_argument("--policy", type=str, default="POLICY_DEFAULT", help="Verification policy ID.")

    # 5. Read-Only Inspection Commands
    inspect_parser = subparsers.add_parser("inspect", help="Read-only inspection of artifacts and capabilities.")
    inspect_parser.add_argument("artifact", help="Artifact ID or backend ID to inspect.")
    inspect_parser.add_argument("--backend", type=str, default=None, help="Backend ID if inspecting backend.")

    lineage_parser = subparsers.add_parser("lineage", help="Read-only visualization of historical provenance chain.")
    lineage_parser.add_argument("artifact", help="Target artifact ID for lineage lookup.")

    return parser


def run_cli(
    args_list: Optional[List[str]] = None,
    service: Optional[ApplicationContractProtocol] = None,
) -> Tuple[int, str]:
    """
    Executes CLI command parsing, Application Contract binding, and response formatting.
    Returns (exit_code, output_text).
    """
    parser = create_cli_parser()

    if args_list is None:
        args_list = sys.argv[1:]

    # Parse arguments
    try:
        parsed_args = parser.parse_args(args_list)
    except SystemExit as se:
        return (int(se.code) if isinstance(se.code, int) else CLIExitCode.INVALID_USER_INPUT.value, "")

    if not parsed_args.command:
        parser.print_help()
        return (CLIExitCode.INVALID_USER_INPUT.value, "Error: No command specified.")

    contract_service = service or ApplicationContractService()
    cmd_enum = CLICommand(parsed_args.command)

    # Build CLIConfig
    config = CLIConfig(output_format=parsed_args.format)

    # Build argument dictionary
    arg_dict = vars(parsed_args).copy()
    if "input" in arg_dict:
        arg_dict["source_code"] = arg_dict.get("input")
    if "artifact" in arg_dict:
        arg_dict["parent_artifact_id"] = arg_dict.get("artifact")
        if cmd_enum == CLICommand.INSPECT and not arg_dict.get("backend"):
            arg_dict["backend"] = arg_dict.get("artifact")
    if "policy" in arg_dict:
        arg_dict["verification_policy_id"] = arg_dict.get("policy")

    # Build ApplicationRequest
    app_request = CLIRequestAdapter.build_request(cmd_enum, arg_dict, config)

    # Dispatch to ApplicationContractService based on command
    if cmd_enum == CLICommand.COMPILE:
        response = contract_service.compile(app_request)
    elif cmd_enum in (CLICommand.AML, CLICommand.UTM, CLICommand.RUTM, CLICommand.SEMANTIC, CLICommand.MAP, CLICommand.OPTIMIZE, CLICommand.LOWER):
        response = contract_service.compile(app_request)
    elif cmd_enum == CLICommand.SIMULATE:
        response = contract_service.simulate(app_request)
    elif cmd_enum == CLICommand.EXECUTE:
        response = contract_service.execute(app_request)
    elif cmd_enum == CLICommand.VERIFY:
        response = contract_service.verify(app_request)
    elif cmd_enum == CLICommand.INSPECT:
        response = contract_service.inspect(app_request)
    elif cmd_enum == CLICommand.LINEAGE:
        response = contract_service.lineage(app_request)
    else:
        return (CLIExitCode.INTERNAL_ERROR.value, f"Unsupported command '{cmd_enum.value}'.")

    exit_code = CLIResponseFormatter.determine_exit_code(response)
    output_text = CLIResponseFormatter.format_output(response, parsed_args.format)

    return (exit_code.value, output_text)


def main() -> None:
    """Production executable main entrypoint."""
    exit_code, output_text = run_cli()
    if output_text:
        print(output_text)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
