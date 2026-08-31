"""
Module 6 Stage 1 — High-Level Analysis Orchestrator.

Provides end-to-end execution of Stage 1 Formal Semantic Mapping & Equivalence Analysis for a given program.
"""

from typing import Dict
from src.module1.utm.model import UTMProgram
from src.module4.foundation.domain import FiniteDomainContract
from src.module6.classical.transition import build_classical_semantic_model
from src.module6.mapping.mapper import CompilerMapper
from src.module6.equivalence.report import SemanticEquivalenceReport
from src.module6.equivalence.verifier import Stage1SemanticVerifier


def analyze_classical_algorithm_stage1(
    program: UTMProgram,
    domain_contract: FiniteDomainContract,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
    algorithm_id: str = "stage1_analysis_alg",
) -> SemanticEquivalenceReport:
    """
    Orchestrates complete Stage 1 semantic correspondence and equivalence analysis:
    1. Builds ClassicalSemanticModel (A_C = A_semantic over D_fin).
    2. Maps A to logical QuantumCircuitIR C_Q using compiler mapping F.
    3. Verifies Level 3 basis equivalence and Level 5 operator equivalence.
    4. Generates structured SemanticEquivalenceReport.
    """
    # 1. Classical Semantic Model Construction
    model = build_classical_semantic_model(
        program=program,
        domain_contract=domain_contract,
        state_map=state_map,
        symbol_map=symbol_map,
        algorithm_id=algorithm_id,
    )

    # 2. Compiler Mapping F Observation
    circuit = CompilerMapper.map_classical_model(
        model=model,
        program=program,
        circuit_id=f"logical_{algorithm_id}",
    )

    # 3. Stage 1 Semantic Verification (Level 3 + Level 5)
    report = Stage1SemanticVerifier.verify_semantic_equivalence(
        model=model,
        circuit=circuit,
    )

    return report
