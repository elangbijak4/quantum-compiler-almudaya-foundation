"""
Dual Execution Orchestration Stage 9: Concurrent Execution via AML Interpreter & UTM Simulator.

Strictly compliant with Stage 9 requirements (main-technical-refference.md Section 7, 25).
"""

from dataclasses import dataclass
from typing import Dict, Optional

from ..aml.parser import parse_aml_source, ParseError, AMLProgram
from ..aml.semantics import AMLState
from ..aml.interpreter import AMLInterpreter, AMLInterpreterResult
from ..translation.encoder import encode_aml_state
from ..translation.translator import translate_aml_to_utm, TranslationResult
from ..utm.simulator import simulate_utm, UTMExecutionResult


@dataclass
class DualExecutionResult:
    """Represents side-by-side results from reference and target execution pathways."""
    aml_result: Optional[AMLInterpreterResult]
    translation_result: Optional[TranslationResult]
    utm_result: Optional[UTMExecutionResult]
    source_hash: str
    status: str  # "DUAL_EXECUTION_COMPLETED", "PARSER_ERROR", "TRANSLATION_ERROR", "SIMULATOR_ERROR"
    error: Optional[str] = None


def execute_dual_pipeline(
    source_text: str,
    initial_memory: Optional[Dict[str, int]] = None,
    aml_max_steps: int = 10000,
    utm_max_steps: int = 100000
) -> DualExecutionResult:
    """
    Orchestrate dual execution of an AML program through both reference (AML Interpreter)
    and target (AML -> UTM -> UTM Simulator) execution pathways.

    Args:
        source_text: Raw AML source text
        initial_memory: Optional initial memory values
        aml_max_steps: Step limit for reference AML interpreter
        utm_max_steps: Step limit for target UTM simulator

    Returns:
        DualExecutionResult containing side-by-side results
    """
    # 1. Parse AML Source Text into AML-IR
    try:
        program: AMLProgram = parse_aml_source(source_text)
    except ParseError as pe:
        return DualExecutionResult(
            aml_result=None,
            translation_result=None,
            utm_result=None,
            source_hash="",
            status="PARSER_ERROR",
            error=str(pe),
        )

    # 2. Pathway A: Reference Execution via AMLInterpreter
    interpreter = AMLInterpreter()
    aml_result: AMLInterpreterResult = interpreter.execute(
        program=program,
        initial_memory=initial_memory,
        max_steps=aml_max_steps,
    )

    # 3. Pathway B1: Translation via AML-IR -> UTM-IR Translator
    translation_result: TranslationResult = translate_aml_to_utm(program)
    if translation_result.status != "TRANSLATION_GENERATED" or not translation_result.utm_program:
        return DualExecutionResult(
            aml_result=aml_result,
            translation_result=translation_result,
            utm_result=None,
            source_hash=program.source_hash,
            status="TRANSLATION_ERROR",
            error=translation_result.error or "UTM translation failed",
        )

    # 4. Pathway B2: Target Execution via UTMSimulator
    # Initialize all referenced symbol table entries in initial memory
    initial_aml_state = AMLState()

    # Pre-populate all memory symbols in program.symbol_table with default 0
    for sym in sorted(list(program.symbol_table)):
        initial_aml_state.memory[sym] = 0

    # Inject explicit initial memory values
    if initial_memory:
        initial_aml_state.memory.update(initial_memory)

    initial_utm_config = encode_aml_state(initial_aml_state)

    utm_result: UTMExecutionResult = simulate_utm(
        program=translation_result.utm_program,
        initial_config=initial_utm_config,
        max_steps=utm_max_steps,
    )

    if utm_result.status == "ERROR" or utm_result.status == "INVALID_TRANSITION":
        return DualExecutionResult(
            aml_result=aml_result,
            translation_result=translation_result,
            utm_result=utm_result,
            source_hash=program.source_hash,
            status="SIMULATOR_ERROR",
            error=utm_result.error or "UTM simulator failed",
        )

    # 5. Package side-by-side execution result
    return DualExecutionResult(
        aml_result=aml_result,
        translation_result=translation_result,
        utm_result=utm_result,
        source_hash=program.source_hash,
        status="DUAL_EXECUTION_COMPLETED",
        error=None,
    )
