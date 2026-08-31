"""
Application / Product Layer — Subpackage Exports.

Exposes application request/response models, contract protocols, contract service implementations,
CLI foundation abstractions, and Research Run / Output Archive abstractions.
"""

from src.application.model import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
)
from src.application.contract import ApplicationContractProtocol
from src.application.service import ApplicationContractService
from src.application.cli import (
    CLIExecutionMode,
    CLICommandCategory,
    CLICommand,
    CLIExitCode,
    CLIConfig,
    CLIRequestAdapter,
    CLIResponseFormatter,
    create_cli_parser,
    run_cli,
    main,
    CLI_VERSION,
)
from src.application.archive import (
    ResearchRunStatus,
    ArchivedArtifact,
    ResearchRun,
    OutputArchiveManager,
)

__all__ = [
    "ApplicationIntent",
    "ApplicationStatus",
    "ApplicationRequest",
    "ApplicationResponse",
    "ApplicationContractProtocol",
    "ApplicationContractService",
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
    "ResearchRunStatus",
    "ArchivedArtifact",
    "ResearchRun",
    "OutputArchiveManager",
]
