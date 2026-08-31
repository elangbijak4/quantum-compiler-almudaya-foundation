"""
UTM-IR -> RUTM-IR Translation Package (Module 2 Stage 6).
"""

from .result import TranslationResult
from .utr_to_rutr import translate_utm_to_rutm, map_utm_configuration_to_rutm

__all__ = [
    "TranslationResult",
    "translate_utm_to_rutm",
    "map_utm_configuration_to_rutm",
]
