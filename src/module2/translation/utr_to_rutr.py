"""
UTM-IR -> RUTM-IR Translator Implementation (Module 2 Stage 6).

Translates a valid classical UTM-IR (UTMProgram) into a valid RUTM-IR machine description
conforming to the proven Stage 1-4 RUTM construction and Stage 5 RUTM-IR model.
"""

from typing import Optional, Dict, Any
from src.module1.utm.model import UTMProgram, UTMConfiguration, validate_utm_program
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm_ir.model import RUTM_IR, RUTMHistoryPolicy, RUTMProvenance
from src.module2.rutm_ir.validator import validate_rutm_ir
from src.module2.translation.result import TranslationResult


def translate_utm_to_rutm(
    program: UTMProgram,
    machine_name: Optional[str] = None,
) -> TranslationResult:
    """
    Translates a valid UTMProgram (UTM-IR) into a valid RUTM_IR machine description.

    Preserves source computational semantics while attaching the Stage 4 proven
    RUTM history policy and proof provenance metadata.

    Returns:
        TranslationResult
    """
    # 1. Validate source UTMProgram
    is_valid_src, src_err = validate_utm_program(program)
    if not is_valid_src:
        return TranslationResult(
            success=False,
            source_program=program,
            target_ir=None,
            errors=(f"Invalid source UTMProgram: {src_err}",),
        )

    # 2. Derive machine name
    name = machine_name if machine_name is not None else "RUTM_Program"

    # 3. Derive input alphabet
    input_alpha = (
        frozenset(s for s in program.alphabet if s != program.blank_symbol)
        if len(program.alphabet) > 1
        else frozenset(program.alphabet)
    )

    # 4. Construct target RUTM_IR
    target_ir = RUTM_IR(
        name=name,
        states=frozenset(program.states),
        input_alphabet=input_alpha,
        tape_alphabet=frozenset(program.alphabet),
        blank_symbol=program.blank_symbol,
        initial_state=program.initial_state,
        halt_state=program.halt_state,
        transitions=dict(program.transitions),
        history_policy=RUTMHistoryPolicy(
            enabled=True,
            record_schema=("prev_state", "overwritten_symbol", "direction"),
            inverse_policy="LIFO_stack",
        ),
        provenance=RUTMProvenance(
            source_model="UTM-IR",
            source_stage="Stage 6",
            proof_reference="docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md",
        ),
    )

    # 5. Validate target RUTM_IR
    is_valid_tgt, tgt_err = validate_rutm_ir(target_ir)
    if not is_valid_tgt:
        return TranslationResult(
            success=False,
            source_program=program,
            target_ir=target_ir,
            errors=(f"Generated RUTM_IR failed validation: {tgt_err}",),
        )

    # 6. Basic structural cost accounting metrics
    metrics = {
        "source_state_count": len(program.states),
        "source_transition_count": len(program.transitions),
        "target_state_count": len(target_ir.states),
        "target_transition_count": len(target_ir.transitions),
        "tape_alphabet_size": len(target_ir.tape_alphabet),
    }

    return TranslationResult(
        success=True,
        source_program=program,
        target_ir=target_ir,
        errors=(),
        warnings=(),
        metrics=metrics,
    )


def map_utm_configuration_to_rutm(
    source_config: UTMConfiguration,
    target_ir: RUTM_IR,
) -> RUTMConfiguration:
    """
    Configuration mapping function E_UR : UTMConfiguration -> RUTMConfiguration.

    Maps a classical UTM configuration to a target RUTM configuration with empty history
    and matching current state, tape, head, step count, halted flag, and error string.
    """
    return RUTMConfiguration(
        current_state=source_config.current_state,
        tape=dict(source_config.tape),
        head_pos=source_config.head_pos,
        history=(),
        step_count=source_config.step_count,
        halted=source_config.halted,
        error=source_config.error,
    )
