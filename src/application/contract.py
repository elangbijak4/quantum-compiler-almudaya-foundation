"""
Application / Product Layer — Application Contract Protocol Interface.

Defines ApplicationContractProtocol exposing compile, inspect, simulate, execute,
verify, and lineage contract methods.
"""

from typing import Protocol
from src.application.model import ApplicationRequest, ApplicationResponse


class ApplicationContractProtocol(Protocol):
    """
    Stable application-facing contract protocol between products and Core.
    """

    def compile(self, request: ApplicationRequest) -> ApplicationResponse:
        """Requests quantum circuit compilation & semantic certification."""
        ...

    def inspect(self, request: ApplicationRequest) -> ApplicationResponse:
        """Requests inspection of Core artifacts (AST, circuit, certificate, lineage)."""
        ...

    def simulate(self, request: ApplicationRequest) -> ApplicationResponse:
        """Requests local virtual reference simulation (Stage 3)."""
        ...

    def execute(self, request: ApplicationRequest) -> ApplicationResponse:
        """Requests provider/cloud execution via provider adapters (Stage 4)."""
        ...

    def verify(self, request: ApplicationRequest) -> ApplicationResponse:
        """Requests statistical result verification against reference distribution (Stage 5)."""
        ...

    def lineage(self, request: ApplicationRequest) -> ApplicationResponse:
        """Requests historical lineage inspection/extension event records (Stage 11)."""
        ...
