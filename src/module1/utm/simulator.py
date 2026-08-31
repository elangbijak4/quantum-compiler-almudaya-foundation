"""
UTM Simulator Stage 8: Single-Step Turing Machine Simulation Engine.

Strictly compliant with Stage 8 requirements (main-technical-refference.md & STAGE_8_UTM_SIMULATOR.md).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .model import (
    UTMProgram,
    UTMConfiguration,
    step_utm_configuration,
)


@dataclass
class UTMExecutionResult:
    """Represents the complete result of executing a UTMProgram on UTMSimulator."""
    final_configuration: UTMConfiguration
    status: str  # "SUCCESS", "RESOURCE_LIMIT", "INVALID_TRANSITION", "ERROR"
    halted: bool
    step_count: int
    tape_usage: int
    trace: Optional[List[Dict[str, Any]]] = None
    execution_trace: Optional[List[UTMConfiguration]] = field(default_factory=list)
    error: Optional[str] = None


class UTMSimulator:
    """
    Faithful single-step simulator for Universal Turing Machine (UTM-IR).
    """

    def execute(
        self,
        program: UTMProgram,
        initial_config: UTMConfiguration,
        max_steps: Optional[int] = 100000,
        enable_trace: bool = False
    ) -> UTMExecutionResult:
        """
        Simulate UTM execution starting from an initial UTMConfiguration.

        Args:
            program: UTMProgram definition
            initial_config: Initial UTMConfiguration C0
            max_steps: Maximum allowed single-step transitions before RESOURCE_LIMIT
            enable_trace: Whether to record step-by-step trace entries

        Returns:
            UTMExecutionResult
        """
        config = UTMConfiguration(
            current_state=initial_config.current_state,
            tape=dict(initial_config.tape),
            head_pos=initial_config.head_pos,
            step_count=initial_config.step_count,
            halted=initial_config.halted,
            error=initial_config.error,
        )

        trace_log: List[Dict[str, Any]] = []
        execution_trace_log: List[UTMConfiguration] = []
        effective_max = max_steps if max_steps is not None else 1_000_000

        def compute_tape_usage(cfg: UTMConfiguration) -> int:
            return sum(1 for v in cfg.tape.values() if v != program.blank_symbol)

        if config.halted or config.current_state == program.halt_state:
            config.halted = True
            return UTMExecutionResult(
                final_configuration=config,
                status="SUCCESS",
                halted=True,
                step_count=config.step_count,
                tape_usage=compute_tape_usage(config),
                trace=trace_log if enable_trace else None,
                execution_trace=execution_trace_log,
            )

        # Execution loop
        while config.step_count < effective_max:
            if enable_trace:
                read_sym = config.get_tape_symbol()
                trace_log.append({
                    "step": config.step_count,
                    "state": config.current_state,
                    "head_pos": config.head_pos,
                    "read_symbol": read_sym,
                })

            next_config = step_utm_configuration(config, program)

            if next_config.error is not None:
                return UTMExecutionResult(
                    final_configuration=next_config,
                    status="INVALID_TRANSITION",
                    halted=False,
                    step_count=next_config.step_count,
                    tape_usage=compute_tape_usage(next_config),
                    trace=trace_log if enable_trace else None,
                    execution_trace=execution_trace_log,
                    error=next_config.error,
                )

            config = next_config
            execution_trace_log.append(config)

            if config.halted or config.current_state == program.halt_state:
                return UTMExecutionResult(
                    final_configuration=config,
                    status="SUCCESS",
                    halted=True,
                    step_count=config.step_count,
                    tape_usage=compute_tape_usage(config),
                    trace=trace_log if enable_trace else None,
                    execution_trace=execution_trace_log,
                )

        # Resource limit reached
        return UTMExecutionResult(
            final_configuration=config,
            status="RESOURCE_LIMIT",
            halted=False,
            step_count=config.step_count,
            tape_usage=compute_tape_usage(config),
            trace=trace_log if enable_trace else None,
            execution_trace=execution_trace_log,
            error=f"Simulation exceeded maximum step count ({effective_max})",
        )


def simulate_utm(
    program: UTMProgram,
    initial_config: UTMConfiguration,
    max_steps: Optional[int] = 100000,
    enable_trace: bool = False
) -> UTMExecutionResult:
    """Convenience functional wrapper for UTMSimulator.execute."""
    simulator = UTMSimulator()
    return simulator.execute(
        program=program,
        initial_config=initial_config,
        max_steps=max_steps,
        enable_trace=enable_trace,
    )
