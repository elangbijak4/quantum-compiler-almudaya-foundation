"""
Module 4 Stage 1 — Register Encoding Specification & Configuration Bitstring Encoding.

Specifies deterministic bit-width allocation for state, tape, head position, history, step counter,
halted status, and error status registers.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
import math
import zlib
from src.module2.rutm.model import RUTMConfiguration
from src.module4.foundation.domain import config_to_key


@dataclass(frozen=True)
class RegisterEncodingSpec:
    """Deterministic width allocation for configuration bitstrings E(C)."""
    n_state: int
    min_tape_pos: int
    max_tape_pos: int
    n_tape_cells: int
    n_bits_per_symbol: int
    n_head_pos: int
    n_history: int
    n_step: int
    n_halted: int = 1
    n_error: int = 1

    @property
    def n_tape_total_bits(self) -> int:
        return self.n_tape_cells * self.n_bits_per_symbol

    @property
    def total_qubits(self) -> int:
        return (
            self.n_state
            + self.n_tape_total_bits
            + self.n_head_pos
            + self.n_history
            + self.n_step
            + self.n_halted
            + self.n_error
        )


def compute_register_encoding_spec(
    domain: List[RUTMConfiguration],
    all_states: Set[str],
    alphabet: Set[str],
) -> RegisterEncodingSpec:
    """Computes minimum qubit register allocation for a given domain D_fin."""
    n_state = max(1, math.ceil(math.log2(max(2, len(all_states)))))
    n_bits_per_symbol = max(1, math.ceil(math.log2(max(2, len(alphabet)))))

    all_positions = []
    max_history_len = 0
    max_step = 0

    for c in domain:
        all_positions.append(c.head_pos)
        if c.tape:
            all_positions.extend(c.tape.keys())
        max_history_len = max(max_history_len, len(c.history))
        max_step = max(max_step, c.step_count)

    min_pos = min(all_positions) if all_positions else 0
    max_pos = max(all_positions) if all_positions else 0
    n_cells = (max_pos - min_pos) + 1

    n_head = max(1, math.ceil(math.log2(max(2, n_cells))))
    n_hist = max(0, max(8, max_history_len * 8)) if max_history_len > 0 else 0
    n_step = max(1, math.ceil(math.log2(max(2, max_step + 1))))

    return RegisterEncodingSpec(
        n_state=n_state,
        min_tape_pos=min_pos,
        max_tape_pos=max_pos,
        n_tape_cells=n_cells,
        n_bits_per_symbol=n_bits_per_symbol,
        n_head_pos=n_head,
        n_history=n_hist,
        n_step=n_step,
        n_halted=1,
        n_error=1,
    )


def encode_configuration(
    config: RUTMConfiguration,
    spec: RegisterEncodingSpec,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
) -> str:
    """
    Computes canonical deterministic bitstring representation E(C) in {0,1}^n.
    """
    # 1. State bitstring
    st_val = state_map.get(config.current_state, 0)
    st_bits = format(st_val, f"0{spec.n_state}b")

    # 2. Tape bitstring for window [M_L, M_R]
    tape_bits_list = []
    for pos in range(spec.min_tape_pos, spec.max_tape_pos + 1):
        sym = config.tape.get(pos, "_")
        sym_val = symbol_map.get(sym, 0)
        tape_bits_list.append(format(sym_val, f"0{spec.n_bits_per_symbol}b"))
    tape_bits = "".join(tape_bits_list)

    # 3. Head pos bitstring (relative to M_L)
    rel_head = config.head_pos - spec.min_tape_pos
    rel_head = max(0, min(rel_head, spec.n_tape_cells - 1))
    head_bits = format(rel_head, f"0{spec.n_head_pos}b")

    # 4. History bitstring (deterministic CRC32 hash of full history tuple)
    if spec.n_history > 0:
        hist_bytes = str(config.history).encode("utf-8")
        hist_val = zlib.crc32(hist_bytes) & ((1 << spec.n_history) - 1)
        hist_bits = format(hist_val, f"0{spec.n_history}b")
    else:
        hist_bits = ""

    # 5. Step count bitstring
    step_bits = format(config.step_count, f"0{spec.n_step}b")

    # 6. Halted & Error bits
    halted_bit = "1" if config.halted else "0"
    error_bit = "1" if config.error else "0"

    return f"{st_bits}{tape_bits}{head_bits}{hist_bits}{step_bits}{halted_bit}{error_bit}"


def verify_encoding_injectivity(
    domain: List[RUTMConfiguration],
    spec: RegisterEncodingSpec,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
) -> bool:
    """Verifies that E(C1) != E(C2) for all distinct C1, C2 in D_fin."""
    seen: Dict[str, RUTMConfiguration] = {}
    for c in domain:
        encoded = encode_configuration(c, spec, state_map, symbol_map)
        if encoded in seen:
            prev = seen[encoded]
            if config_to_key(prev) != config_to_key(c):
                return False  # Collision detected!
        seen[encoded] = c
    return True
