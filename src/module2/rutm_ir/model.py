"""
RUTM-IR Model Definition (Module 2 Stage 5).

Compiler-oriented Intermediate Representation (IR) of the Reversible Universal Turing Machine (RUTM).
Strictly compliant with Stage 5 requirements (main-technical-refference.md & STAGE_5_RUTM_IR.md).
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Set, Optional, Any, FrozenSet
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration, create_initial_rutm_configuration


@dataclass(frozen=True)
class RUTMHistoryPolicy:
    """Static History Policy metadata for RUTM-IR."""

    enabled: bool = True
    record_schema: Tuple[str, ...] = ("prev_state", "overwritten_symbol", "direction")
    inverse_policy: str = "LIFO_stack"


@dataclass(frozen=True)
class RUTMProvenance:
    """Static Proof Provenance metadata for RUTM-IR."""

    source_model: str = "RUTM"
    source_stage: str = "Stage 4"
    proof_reference: str = "docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md"
    specification_version: str = "2.0"


@dataclass(frozen=True)
class RUTM_IR:
    """
    Compiler-level Intermediate Representation of a Reversible Universal Turing Machine.

    Tuple representation:
        RUTM_IR = (name, Q, Σ, Γ, B, q_start, q_halt, δ_R, history_policy, provenance)
    """

    name: str
    states: FrozenSet[str]
    input_alphabet: FrozenSet[str]
    tape_alphabet: FrozenSet[str]
    blank_symbol: str
    initial_state: str
    halt_state: str
    transitions: Dict[Tuple[str, str], TransitionAction]
    history_policy: RUTMHistoryPolicy = field(default_factory=RUTMHistoryPolicy)
    provenance: RUTMProvenance = field(default_factory=RUTMProvenance)

    def to_utm_program(self) -> UTMProgram:
        """
        Converts the RUTM_IR machine description into an executable UTMProgram object.

        Maintains exact semantic identity with Module 1 / Stage 1-4 models.
        """
        return UTMProgram(
            states=set(self.states),
            alphabet=set(self.tape_alphabet),
            blank_symbol=self.blank_symbol,
            initial_state=self.initial_state,
            halt_state=self.halt_state,
            transitions=dict(self.transitions),
        )


def create_initial_configuration_from_ir(
    ir: RUTM_IR,
    tape: Optional[Dict[int, str]] = None,
) -> RUTMConfiguration:
    """
    Constructs an initial RUTMConfiguration from a static RUTM_IR machine description.

    Reuses frozen Stage 2 create_initial_rutm_configuration constructor.
    """
    return create_initial_rutm_configuration(
        tape=tape if tape is not None else {},
        initial_state=ir.initial_state,
    )
