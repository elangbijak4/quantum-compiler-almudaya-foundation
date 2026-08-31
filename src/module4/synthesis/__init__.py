"""
Module 4 Synthesis Package — Logical Reversible Synthesis & Verification.
"""

from src.module4.synthesis.transition import (
    TransitionPair,
    TransitionTable,
    build_transition_table,
)
from src.module4.synthesis.ancilla import (
    AncillaManager,
    synthesize_multi_controlled_not,
)
from src.module4.synthesis.reversible import (
    synthesize_qtm_transition,
)
from src.module4.synthesis.verifier import (
    Stage3VerificationResult,
    verify_transition_realization,
    execute_circuit_on_bitstring,
    execute_inverse_circuit_on_bitstring,
)

__all__ = [
    "TransitionPair",
    "TransitionTable",
    "build_transition_table",
    "AncillaManager",
    "synthesize_multi_controlled_not",
    "synthesize_qtm_transition",
    "Stage3VerificationResult",
    "verify_transition_realization",
    "execute_circuit_on_bitstring",
    "execute_inverse_circuit_on_bitstring",
]
