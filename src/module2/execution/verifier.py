"""
Trace and Differential Verification Utilities (Module 2 Stage 7).

Provides finite-trace reversibility verification via frozen reverse_step_rutm()
and differential UTM/RUTM projection verification via frozen project_to_utm().
"""

from typing import Optional
from src.module1.utm.model import UTMProgram, UTMConfiguration, step_utm_configuration
from src.module2.rutm.model import project_to_utm, RUTMConfiguration
from src.module2.rutm.semantics import reverse_step_rutm
from src.module2.rutm_ir.model import RUTM_IR
from src.module2.execution.result import (
    RUTMExecutionResult,
    ReversibilityVerificationResult,
    DifferentialVerificationResult,
)


def verify_trace_reversibility(
    execution_result: RUTMExecutionResult,
    target_ir: RUTM_IR,
) -> ReversibilityVerificationResult:
    """
    Verifies that a completed RUTM execution trace is 100% reversible step-by-step
    back to its initial configuration C_0 using frozen reverse_step_rutm().

    Returns:
        ReversibilityVerificationResult
    """
    trace = execution_result.trace
    if not trace:
        return ReversibilityVerificationResult(
            verified=False,
            original_configuration=RUTMConfiguration(),
            restored_configuration=RUTMConfiguration(),
            forward_steps=0,
            reverse_steps=0,
            error="Empty trace provided for reversibility verification",
        )

    program = target_ir.to_utm_program()
    curr = trace[-1]
    reverse_steps = 0

    # Reverse trace pairwise step-by-step
    for idx in range(len(trace) - 1, 0, -1):
        expected_prev = trace[idx - 1]
        restored_prev = reverse_step_rutm(curr, program)

        if restored_prev != expected_prev:
            return ReversibilityVerificationResult(
                verified=False,
                original_configuration=trace[0],
                restored_configuration=restored_prev,
                forward_steps=execution_result.steps_executed,
                reverse_steps=reverse_steps,
                failure_index=idx - 1,
                error=f"Reversal mismatch at trace index {idx - 1}: expected {expected_prev}, got {restored_prev}",
            )

        curr = restored_prev
        reverse_steps += 1

    # Check final restored configuration matches original C_0
    is_restored = (curr == trace[0])
    return ReversibilityVerificationResult(
        verified=is_restored,
        original_configuration=trace[0],
        restored_configuration=curr,
        forward_steps=execution_result.steps_executed,
        reverse_steps=reverse_steps,
        failure_index=None if is_restored else 0,
        error=None if is_restored else "Restored configuration does not match original C_0",
    )


def verify_projected_utm_correspondence(
    rutm_result: RUTMExecutionResult,
    utm_program: UTMProgram,
    initial_utm_config: UTMConfiguration,
) -> DifferentialVerificationResult:
    """
    Performs differential step-by-step verification comparing projected RUTM execution
    pi_UTM(C_R, i) against classical source UTM execution C_U, i.

    Returns:
        DifferentialVerificationResult
    """
    trace = rutm_result.trace
    if not trace:
        return DifferentialVerificationResult(
            matched=False,
            steps_compared=0,
            error="Empty RUTM execution trace provided",
        )

    curr_utm = UTMConfiguration(
        current_state=initial_utm_config.current_state,
        tape=dict(initial_utm_config.tape),
        head_pos=initial_utm_config.head_pos,
        step_count=initial_utm_config.step_count,
        halted=initial_utm_config.halted,
        error=initial_utm_config.error,
    )

    for i, rutm_config in enumerate(trace):
        projected_rutm = project_to_utm(rutm_config)

        if projected_rutm != curr_utm:
            return DifferentialVerificationResult(
                matched=False,
                steps_compared=i + 1,
                mismatch_step=i,
                utm_configuration=curr_utm,
                projected_rutm_configuration=projected_rutm,
                error=f"Projection mismatch at trace step {i}: UTM={curr_utm}, RUTM_proj={projected_rutm}",
            )

        # Advance classical UTM to next step if not at trace end
        if i < len(trace) - 1:
            curr_utm = step_utm_configuration(curr_utm, utm_program)

    return DifferentialVerificationResult(
        matched=True,
        steps_compared=len(trace),
        mismatch_step=None,
        utm_configuration=None,
        projected_rutm_configuration=None,
        error=None,
    )
