"""
AML v0.1 Interpreter: Reference Executable Semantics (Sem_AML).

Strictly compliant with Stage 5 requirements (main-technical-refference.md Section 8, 18, 25).
"""

from dataclasses import dataclass
from typing import Dict, Optional

from .semantics import AMLState, step_operational_semantics
from .parser import AMLProgram, parse_aml_source


@dataclass
class AMLInterpreterResult:
    """Represents the complete execution result of the AML Interpreter."""
    final_state: AMLState
    observable_output: Dict[str, int]
    step_count: int
    status: str  # "SUCCESS", "RESOURCE_LIMIT", "ERROR"


class AMLInterpreter:
    """
    Reference executable semantics interpreter for AML programs.
    """

    def execute(
        self,
        program: AMLProgram,
        initial_memory: Optional[Dict[str, int]] = None,
        max_steps: int = 10000
    ) -> AMLInterpreterResult:
        """
        Execute an AMLProgram (AML-IR) using small-step operational semantics.

        Args:
            program: Parsed AMLProgram (AML-IR)
            initial_memory: Optional initial memory values
            max_steps: Maximum allowed execution steps before hitting RESOURCE_LIMIT

        Returns:
            AMLInterpreterResult
        """
        # 1. Initialize Machine State S0
        state = AMLState()
        if initial_memory:
            state.memory.update(initial_memory)

        step_count = 0
        total_instructions = len(program.instructions)

        # 2. Sequential Execution Loop
        while step_count < max_steps:
            # Check for HALT
            if state.flags.halted:
                return AMLInterpreterResult(
                    final_state=state,
                    observable_output=dict(state.memory),
                    step_count=step_count,
                    status="SUCCESS",
                )

            # Check for operational error
            if state.flags.error:
                return AMLInterpreterResult(
                    final_state=state,
                    observable_output=dict(state.memory),
                    step_count=step_count,
                    status="ERROR",
                )

            # PC boundary check
            if state.pc < 0 or state.pc >= total_instructions:
                state.flags.error = f"Program Counter out of bounds: PC={state.pc}, Total={total_instructions}"
                return AMLInterpreterResult(
                    final_state=state,
                    observable_output=dict(state.memory),
                    step_count=step_count,
                    status="ERROR",
                )

            # Fetch current instruction
            current_instr = program.instructions[state.pc]

            # Step operational semantics
            state = step_operational_semantics(
                state=state,
                opcode_str=current_instr.opcode.value,
                operands=current_instr.operands,
                label_table=program.label_table,
            )

            step_count += 1

        # Check for final HALT on exactly max_steps boundary
        if state.flags.halted:
            return AMLInterpreterResult(
                final_state=state,
                observable_output=dict(state.memory),
                step_count=step_count,
                status="SUCCESS",
            )

        # Exceeded step limit
        return AMLInterpreterResult(
            final_state=state,
            observable_output=dict(state.memory),
            step_count=step_count,
            status="RESOURCE_LIMIT",
        )


def execute_aml_source(
    source_text: str,
    initial_memory: Optional[Dict[str, int]] = None,
    max_steps: int = 10000
) -> AMLInterpreterResult:
    """
    Convenience function: Parse AML source text and execute via AMLInterpreter.
    """
    program = parse_aml_source(source_text)
    interpreter = AMLInterpreter()
    return interpreter.execute(program, initial_memory, max_steps)
