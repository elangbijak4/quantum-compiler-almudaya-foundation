"""
RUTM-IR Execution Engine Implementation (Module 2 Stage 7).

Orchestrates multi-step forward execution of static RUTM-IR descriptions using frozen Stage 3
operational semantics. Collects immutable configuration traces, enforces resource bounds, and
handles halting/error detection.
"""

from typing import Optional, Dict, List
from src.module2.rutm.model import RUTMConfiguration, create_initial_rutm_configuration
from src.module2.rutm.semantics import forward_step_rutm, valid_rutm_configuration
from src.module2.rutm_ir.model import RUTM_IR, create_initial_configuration_from_ir
from src.module2.rutm_ir.validator import validate_rutm_ir
from src.module2.execution.result import RUTMExecutionResult


def execute_rutm_ir(
    target_ir: RUTM_IR,
    initial_tape: Optional[Dict[int, str]] = None,
    initial_config: Optional[RUTMConfiguration] = None,
    max_steps: int = 1000,
) -> RUTMExecutionResult:
    """
    Executes a static RUTM-IR machine description up to max_steps or terminal halting/error.

    Reuses frozen Stage 3 operational semantics (forward_step_rutm).
    Preserves trace immutability by snapshotting configurations at every step.

    Returns:
        RUTMExecutionResult
    """
    # 1. Pre-execution static IR validation
    is_valid_ir, ir_err = validate_rutm_ir(target_ir)
    if not is_valid_ir:
        dummy_config = RUTMConfiguration(current_state=target_ir.initial_state)
        return RUTMExecutionResult(
            success=False,
            initial_configuration=dummy_config,
            final_configuration=dummy_config,
            trace=(dummy_config,),
            steps_executed=0,
            halted=False,
            error=f"Invalid RUTM_IR: {ir_err}",
            resource_limit_reached=False,
        )

    # 2. Derive program context from static IR
    program = target_ir.to_utm_program()

    # 3. Construct or validate initial configuration
    if initial_config is None:
        current_config = create_initial_configuration_from_ir(target_ir, tape=initial_tape)
    else:
        current_config = RUTMConfiguration(
            current_state=initial_config.current_state,
            tape=dict(initial_config.tape),
            head_pos=initial_config.head_pos,
            history=initial_config.history,
            step_count=initial_config.step_count,
            halted=initial_config.halted,
            error=initial_config.error,
        )

    # 4. Pre-validate initial configuration against program context
    is_valid_cfg, cfg_err = valid_rutm_configuration(
        current_config, program.states, program.alphabet, program.halt_state
    )
    if not is_valid_cfg:
        return RUTMExecutionResult(
            success=False,
            initial_configuration=current_config,
            final_configuration=current_config,
            trace=(current_config,),
            steps_executed=0,
            halted=False,
            error=f"Invalid initial configuration: {cfg_err}",
            resource_limit_reached=False,
        )

    # 5. Initialize trace collection with an immutable copy of C_0
    trace: List[RUTMConfiguration] = [
        RUTMConfiguration(
            current_state=current_config.current_state,
            tape=dict(current_config.tape),
            head_pos=current_config.head_pos,
            history=current_config.history,
            step_count=current_config.step_count,
            halted=current_config.halted,
            error=current_config.error,
        )
    ]

    # 6. Multi-step execution loop
    steps_executed = 0
    while steps_executed < max_steps:
        # Terminal checks BEFORE attempting forward step
        if current_config.halted or current_config.current_state == program.halt_state:
            break
        if current_config.error is not None:
            break

        # Execute single forward step using frozen Stage 3 semantics
        next_config = forward_step_rutm(current_config, program)

        # Snapshot new configuration into trace (deep copy of tape/history dict/tuple)
        trace_entry = RUTMConfiguration(
            current_state=next_config.current_state,
            tape=dict(next_config.tape),
            head_pos=next_config.head_pos,
            history=next_config.history,
            step_count=next_config.step_count,
            halted=next_config.halted,
            error=next_config.error,
        )
        trace.append(trace_entry)
        current_config = next_config
        steps_executed += 1

        # Terminal check AFTER forward step
        if next_config.error is not None or next_config.halted:
            break

    # 7. Final status classification
    final_cfg = trace[-1]
    is_halted = final_cfg.halted or (final_cfg.current_state == program.halt_state and final_cfg.error is None)
    has_error = final_cfg.error is not None
    resource_limit_reached = (not is_halted) and (not has_error) and (steps_executed >= max_steps)

    return RUTMExecutionResult(
        success=(not has_error),
        initial_configuration=trace[0],
        final_configuration=final_cfg,
        trace=tuple(trace),
        steps_executed=steps_executed,
        halted=is_halted,
        error=final_cfg.error,
        resource_limit_reached=resource_limit_reached,
    )
