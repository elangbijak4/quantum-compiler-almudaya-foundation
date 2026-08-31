"""
Module 6 Stage 1 — Basis Correspondence Data Record.

Represents individual basis state semantic correspondence evaluation results
for a configuration C in D_fin under the compiler mapping F.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BasisCorrespondenceRecord:
    """
    Individual basis correspondence evaluation record for a configuration C in D_fin.
    """
    index: int
    config_id: str
    config_category: str  # "INITIAL", "INTERNAL", "HALTING", "ERROR"
    encoded_input_bits: str
    classical_successor_bits: str
    quantum_output_bits: str
    expected_output_bits: str
    residual_l2: float
    passed: bool
    is_symbolic_exact: bool = True
    error_message: Optional[str] = None
