"""
Module 6 Stage 6 — Compiler Context & Result Integration Subpackage.
"""

from src.module6.integration.result import (
    CompilationStatus,
    EquivalenceStatus,
    EquivalenceLevel,
    CompilationResult,
    serialize_compilation_result,
    deserialize_compilation_result,
)
from src.module6.integration.context import CompilerContext

__all__ = [
    "CompilationStatus",
    "EquivalenceStatus",
    "EquivalenceLevel",
    "CompilationResult",
    "serialize_compilation_result",
    "deserialize_compilation_result",
    "CompilerContext",
]
