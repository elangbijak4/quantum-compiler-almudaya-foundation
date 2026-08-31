"""
Module 4 Foundation — Finite Domain Contract & Validation.

Specifies the finite configuration domain D_fin ⊂ C_R and verifies forward/reverse closure under R_P.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Tuple, Any
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module1.utm.model import UTMProgram


def config_to_key(c: RUTMConfiguration) -> Tuple[Any, ...]:
    """Helper converting RUTMConfiguration to an immutable hashable tuple."""
    tape_tuple = tuple(sorted((k, v) for k, v in c.tape.items() if v != "_"))
    return (c.current_state, tape_tuple, c.head_pos, c.history, c.step_count, c.halted, c.error)


@dataclass(frozen=True)
class FiniteDomainValidationResult:
    """Outcome of validating a FiniteDomainContract."""
    valid: bool
    cardinality: int
    forward_closed: bool
    reverse_closed: bool
    contains_initial: bool
    diagnostics: List[str] = field(default_factory=list)


@dataclass
class FiniteDomainContract:
    """
    Formal contract specifying a finite configuration domain D_fin ⊂ C_R.
    
    Invariants:
    1. |D_fin| < ∞
    2. R_P(D_fin) ⊆ D_fin (Forward Closure)
    3. R_P^{-1}(D_fin) ⊆ D_fin (Reverse Closure)
    """
    domain: List[RUTMConfiguration]
    execution_horizon: int
    initial_configuration: Optional[RUTMConfiguration] = None
    description: str = "Finite QTM-IR Realization Domain"

    @property
    def cardinality(self) -> int:
        return len(self.domain)

    def validate(self, program: UTMProgram) -> FiniteDomainValidationResult:
        """Validates that D_fin is finite, non-empty, forward-closed, and reverse-closed under R_P."""
        diagnostics = []
        if len(self.domain) == 0:
            return FiniteDomainValidationResult(
                valid=False, cardinality=0, forward_closed=False, reverse_closed=False, contains_initial=False,
                diagnostics=["Domain is empty."]
            )

        # Config lookup set by exact structural key
        config_set: Set[Tuple[Any, ...]] = {config_to_key(c) for c in self.domain}

        forward_closed = True
        reverse_closed = True

        for config in self.domain:
            # 1. Forward step (config, program)
            fwd_c = forward_step_rutm(config, program)
            fwd_key = config_to_key(fwd_c)
            if fwd_key not in config_set:
                # If halted, terminal fixed point
                if not (config.halted or config.current_state == program.halt_state):
                    forward_closed = False
                    diagnostics.append(f"Forward step escapes domain: {config} -> {fwd_c}")

            # 2. Reverse step (config, program)
            if len(config.history) > 0:
                try:
                    rev_c = reverse_step_rutm(config, program)
                    rev_key = config_to_key(rev_c)
                    if rev_key not in config_set:
                        reverse_closed = False
                        diagnostics.append(f"Reverse step escapes domain: {config} -> {rev_c}")
                except Exception as e:
                    reverse_closed = False
                    diagnostics.append(f"Reverse step failed for configuration {config}: {e}")

        contains_init = True
        if self.initial_configuration is not None:
            contains_init = config_to_key(self.initial_configuration) in config_set
            if not contains_init:
                diagnostics.append(f"Initial configuration missing from domain.")

        valid = forward_closed and reverse_closed and contains_init

        return FiniteDomainValidationResult(
            valid=valid,
            cardinality=len(self.domain),
            forward_closed=forward_closed,
            reverse_closed=reverse_closed,
            contains_initial=contains_init,
            diagnostics=diagnostics,
        )
