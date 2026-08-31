"""
Application / Product Layer — CLI Subpackage Exports.

Exposes CLIExecutionMode, CLICommandCategory, CLICommand, CLIExitCode, CLIConfig,
CLIRequestAdapter, CLIResponseFormatter, create_cli_parser, run_cli, main, and CLI_VERSION.
"""

from src.application.cli.model import (
    CLIExecutionMode,
    CLICommandCategory,
    CLICommand,
    CLIExitCode,
    CLIConfig,
    CLIRequestAdapter,
    CLIResponseFormatter,
)
from src.application.cli.main import (
    create_cli_parser,
    run_cli,
    main,
    CLI_VERSION,
)

__all__ = [
    "CLIExecutionMode",
    "CLICommandCategory",
    "CLICommand",
    "CLIExitCode",
    "CLIConfig",
    "CLIRequestAdapter",
    "CLIResponseFormatter",
    "create_cli_parser",
    "run_cli",
    "main",
    "CLI_VERSION",
]
