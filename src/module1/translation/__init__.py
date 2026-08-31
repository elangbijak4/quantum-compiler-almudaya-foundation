"""
Translation Module: AML-IR to UTM-IR Compiler Transformation.
"""

from .encoder import (
    TAPE_START_MARKER,
    TAPE_PC_MARKER,
    TAPE_ZERO_FLAG_MARKER,
    TAPE_HALT_FLAG_MARKER,
    TAPE_SECTION_DELIMITER,
    TAPE_MEM_MARKER,
    encode_aml_state,
    decode_aml_state,
)

from .translator import (
    TranslationResult,
    translate_aml_to_utm,
)

__all__ = [
    "TAPE_START_MARKER",
    "TAPE_PC_MARKER",
    "TAPE_ZERO_FLAG_MARKER",
    "TAPE_HALT_FLAG_MARKER",
    "TAPE_SECTION_DELIMITER",
    "TAPE_MEM_MARKER",
    "encode_aml_state",
    "decode_aml_state",
    "TranslationResult",
    "translate_aml_to_utm",
]
