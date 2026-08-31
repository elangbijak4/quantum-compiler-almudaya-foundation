"""
Quantum Computational Basis Model (Module 3 Stage 2).

Defines the computational basis representation |C_R⟩ for valid RUTM configurations C_R,
the embedding function ι(C_R) = |C_R⟩, and computational basis inner-product orthogonality.
"""

from typing import Tuple, Dict, Any, Optional
from src.module2.rutm.model import RUTMConfiguration, valid_rutm_configuration


class QuantumBasisState:
    """
    Representation of a quantum computational basis state |C_R⟩ corresponding
    to a classical Reversible Universal Turing Machine configuration C_R.

    Preserves semantic identity of the underlying RUTM configuration.
    """

    __slots__ = ("_config", "_canonical_key")

    def __init__(self, config: RUTMConfiguration) -> None:
        """
        Initializes a quantum basis state |C_R⟩.

        :param config: Valid RUTMConfiguration instance from Module 2.
        :raises TypeError: If config is not a RUTMConfiguration instance.
        :raises ValueError: If config fails valid_rutm_configuration validation.
        """
        if not isinstance(config, RUTMConfiguration):
            raise TypeError("QuantumBasisState requires a valid RUTMConfiguration instance.")

        is_valid, err_msg = valid_rutm_configuration(config)
        if not is_valid:
            raise ValueError(f"Invalid RUTMConfiguration for basis state: {err_msg}")

        self._config = config
        self._canonical_key = self._make_canonical_key(config)

    @staticmethod
    def _make_canonical_key(config: RUTMConfiguration) -> Tuple[Any, ...]:
        """
        Generates a canonical hashable key capturing the full semantic identity
        of the underlying RUTMConfiguration.
        """
        tape_items = tuple(sorted((k, v) for k, v in config.tape.items() if v != "_"))
        history_items = tuple(
            (rec.prev_state, rec.overwritten_symbol, rec.direction)
            for rec in config.history
        )
        return (
            config.current_state,
            tape_items,
            config.head_pos,
            history_items,
            config.step_count,
            config.halted,
            config.error,
        )

    @property
    def config(self) -> RUTMConfiguration:
        """Returns the underlying RUTMConfiguration instance."""
        return self._config

    @property
    def canonical_key(self) -> Tuple[Any, ...]:
        """Returns the canonical tuple key of the underlying configuration."""
        return self._canonical_key

    def __hash__(self) -> int:
        return hash(self._canonical_key)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, QuantumBasisState):
            return False
        return self._canonical_key == other._canonical_key

    def __repr__(self) -> str:
        state = self._config.current_state
        head = self._config.head_pos
        k = len(self._config.history)
        halted = "H" if self._config.halted else "R"
        return f"|C_R({state}, h={head}, k={k}, {halted})⟩"


def iota(config: RUTMConfiguration) -> QuantumBasisState:
    """
    Formal configuration embedding function ι : C_R -> H_Q.

    Maps classical configuration C_R to quantum computational basis state |C_R⟩.

    :param config: Valid RUTMConfiguration instance.
    :return: QuantumBasisState |C_R⟩.
    """
    return QuantumBasisState(config)


def basis_inner_product(
    b1: QuantumBasisState, b2: QuantumBasisState
) -> complex:
    """
    Computes Dirac inner product ⟨C_1 | C_2⟩ between two computational basis states.

    Enforces orthogonality invariant: ⟨C_1 | C_2⟩ = δ(C_1, C_2).

    :param b1: Basis state |C_1⟩.
    :param b2: Basis state |C_2⟩.
    :return: 1.0 + 0.0j if b1 == b2, else 0.0 + 0.0j.
    """
    if not isinstance(b1, QuantumBasisState) or not isinstance(b2, QuantumBasisState):
        raise TypeError("basis_inner_product requires QuantumBasisState arguments.")
    return complex(1.0 if b1 == b2 else 0.0)
