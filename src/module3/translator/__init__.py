"""
Module 3 Translator Package — RUTM-IR -> QTM-IR Translator (T_RQ).
"""

from src.module3.translator.rutm_to_qtm import (
    RUTMToQTMTranslator,
    RUTMToQTMTranslationError,
    translate_rutm_to_qtm_ir,
    compute_canonical_basis_id,
    lift_configuration,
    compute_source_program_hash,
    verify_forward_commuting_relation,
    verify_reverse_commuting_relation,
)

__all__ = [
    "RUTMToQTMTranslator",
    "RUTMToQTMTranslationError",
    "translate_rutm_to_qtm_ir",
    "compute_canonical_basis_id",
    "lift_configuration",
    "compute_source_program_hash",
    "verify_forward_commuting_relation",
    "verify_reverse_commuting_relation",
]
