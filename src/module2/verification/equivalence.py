"""
UTM -> RUTM Equivalence Verification Gate Implementation (Module 2 Stage 8).

Constructs the complete end-to-end verification gate determining whether a translated RUTM
computation preserves the observable behavior of its source UTM computation over a defined
finite execution domain.

Reuses:
- Module 1 UTM semantics (validate_utm_program, step_utm_configuration)
- Stage 4 projection theorem (project_to_utm)
- Stage 6 translator (translate_utm_to_rutm, map_utm_configuration_to_rutm)
- Stage 7 executor (execute_rutm_ir)
"""

from typing import Optional, Dict, Any
from src.module1.utm.model import UTMProgram, UTMConfiguration, validate_utm_program, step_utm_configuration
from src.module2.rutm.model import project_to_utm, RUTMConfiguration
from src.module2.rutm_ir.validator import validate_rutm_ir
from src.module2.translation.utr_to_rutr import translate_utm_to_rutm, map_utm_configuration_to_rutm
from src.module2.execution.executor import execute_rutm_ir
from src.module2.verification.result import EquivalenceVerificationResult


def verify_utm_to_rutm_equivalence(
    utm_program: UTMProgram,
    initial_utm_config: Optional[UTMConfiguration] = None,
    max_steps: int = 1000,
) -> EquivalenceVerificationResult:
    """
    Complete end-to-end UTM -> RUTM equivalence verification gate.

    Determines finite trace equivalence between a source classical UTM and its translated RUTM.
    Classifies outcomes distinctly into PASS, FAIL, or INCONCLUSIVE.

    Returns:
        EquivalenceVerificationResult
    """
    # 1. Source UTM Validation
    is_valid_src, src_err = validate_utm_program(utm_program)
    if not is_valid_src:
        return EquivalenceVerificationResult(
            status="FAIL",
            equivalent=False,
            steps_compared=0,
            source_trace_length=0,
            target_trace_length=0,
            error=f"Invalid source UTMProgram: {src_err}",
        )

    # 2. UTM -> RUTM Translation
    trans_res = translate_utm_to_rutm(utm_program)
    if not trans_res.success or trans_res.target_ir is None:
        err_msg = trans_res.errors[0] if trans_res.errors else "Translation failed"
        return EquivalenceVerificationResult(
            status="FAIL",
            equivalent=False,
            steps_compared=0,
            source_trace_length=0,
            target_trace_length=0,
            error=f"Translation failure: {err_msg}",
        )

    target_ir = trans_res.target_ir

    # 3. Target RUTM-IR Validation
    is_valid_tgt, tgt_err = validate_rutm_ir(target_ir)
    if not is_valid_tgt:
        return EquivalenceVerificationResult(
            status="FAIL",
            equivalent=False,
            steps_compared=0,
            source_trace_length=0,
            target_trace_length=0,
            error=f"Generated RUTM_IR failed validation: {tgt_err}",
        )

    # 4. Construct / Validate initial configurations
    if initial_utm_config is None:
        c0_utm = UTMConfiguration(
            current_state=utm_program.initial_state,
            tape={},
            head_pos=0,
            step_count=0,
            halted=False,
            error=None,
        )
    else:
        c0_utm = UTMConfiguration(
            current_state=initial_utm_config.current_state,
            tape=dict(initial_utm_config.tape),
            head_pos=initial_utm_config.head_pos,
            step_count=initial_utm_config.step_count,
            halted=initial_utm_config.halted,
            error=initial_utm_config.error,
        )

    c0_rutm = map_utm_configuration_to_rutm(c0_utm, target_ir)

    # 5. Initial Configuration Correspondence Check
    proj_c0 = project_to_utm(c0_rutm)
    if proj_c0 != c0_utm:
        return EquivalenceVerificationResult(
            status="FAIL",
            equivalent=False,
            steps_compared=1,
            source_trace_length=1,
            target_trace_length=1,
            mismatch_step=0,
            source_configuration=c0_utm,
            target_configuration=c0_rutm,
            projected_target_configuration=proj_c0,
            error="Initial configuration projection mismatch",
        )

    # 6. Execute Source UTM Trace up to max_steps
    source_trace = [c0_utm]
    curr_utm = c0_utm
    src_steps = 0

    while src_steps < max_steps:
        if curr_utm.halted or curr_utm.current_state == utm_program.halt_state or curr_utm.error is not None:
            break
        next_utm = step_utm_configuration(curr_utm, utm_program)
        source_trace.append(next_utm)
        curr_utm = next_utm
        src_steps += 1
        if curr_utm.error is not None or curr_utm.halted:
            break

    # 7. Execute Target RUTM Trace up to max_steps
    rutm_res = execute_rutm_ir(target_ir, initial_config=c0_rutm, max_steps=max_steps)
    if not rutm_res.success and rutm_res.error is not None and not rutm_res.resource_limit_reached:
        return EquivalenceVerificationResult(
            status="FAIL",
            equivalent=False,
            steps_compared=len(rutm_res.trace),
            source_trace_length=len(source_trace),
            target_trace_length=len(rutm_res.trace),
            mismatch_step=len(rutm_res.trace) - 1,
            error=f"Target RUTM execution runtime error: {rutm_res.error}",
        )

    # 8. Differential Step-by-Step Equivalence Check
    steps_to_compare = min(len(source_trace), len(rutm_res.trace))
    for i in range(steps_to_compare):
        u_cfg = source_trace[i]
        r_cfg = rutm_res.trace[i]
        p_cfg = project_to_utm(r_cfg)

        if p_cfg != u_cfg:
            return EquivalenceVerificationResult(
                status="FAIL",
                equivalent=False,
                steps_compared=i + 1,
                source_trace_length=len(source_trace),
                target_trace_length=len(rutm_res.trace),
                mismatch_step=i,
                source_configuration=u_cfg,
                target_configuration=r_cfg,
                projected_target_configuration=p_cfg,
                error=f"Semantic mismatch at step {i}: state/tape/head/step mismatch",
            )

    # 9. Terminal Classification (PASS vs FAIL vs INCONCLUSIVE)
    src_final = source_trace[-1]
    tgt_final = rutm_res.final_configuration

    src_halted = src_final.halted or (src_final.current_state == utm_program.halt_state and src_final.error is None)
    tgt_halted = rutm_res.halted

    provenance_data = {
        "source_model": "UTM-IR",
        "source_stage": "Stage 6",
        "proof_reference": target_ir.provenance.proof_reference,
        "gate_stage": "Stage 8",
    }

    # Case A: Both halted normally and trace lengths match -> PASS
    if src_halted and tgt_halted and len(source_trace) == len(rutm_res.trace):
        return EquivalenceVerificationResult(
            status="PASS",
            equivalent=True,
            steps_compared=len(source_trace),
            source_trace_length=len(source_trace),
            target_trace_length=len(rutm_res.trace),
            source_halted=True,
            target_halted=True,
            resource_limit_reached=False,
            error=None,
            provenance=provenance_data,
        )

    # Case B: Terminal halt correspondence mismatch -> FAIL (Precedence: actual mismatch > resource exhaustion)
    if src_halted != tgt_halted:
        return EquivalenceVerificationResult(
            status="FAIL",
            equivalent=False,
            steps_compared=steps_to_compare,
            source_trace_length=len(source_trace),
            target_trace_length=len(rutm_res.trace),
            mismatch_step=steps_to_compare - 1,
            source_halted=src_halted,
            target_halted=tgt_halted,
            error=f"Halt correspondence mismatch: source_halted={src_halted}, target_halted={tgt_halted}",
            provenance=provenance_data,
        )

    # Case C: Resource exhaustion before halting (neither halted, no trace mismatch) -> INCONCLUSIVE
    if not src_halted and not tgt_halted:
        return EquivalenceVerificationResult(
            status="INCONCLUSIVE",
            equivalent=False,
            steps_compared=steps_to_compare,
            source_trace_length=len(source_trace),
            target_trace_length=len(rutm_res.trace),
            source_halted=False,
            target_halted=False,
            resource_limit_reached=True,
            error=None,
            provenance=provenance_data,
        )

    # Case D: Default fail if unhandled trace length discrepancy
    return EquivalenceVerificationResult(
        status="FAIL",
        equivalent=False,
        steps_compared=steps_to_compare,
        source_trace_length=len(source_trace),
        target_trace_length=len(rutm_res.trace),
        mismatch_step=steps_to_compare - 1,
        source_halted=src_halted,
        target_halted=tgt_halted,
        error="Execution or trace length correspondence failed",
        provenance=provenance_data,
    )
