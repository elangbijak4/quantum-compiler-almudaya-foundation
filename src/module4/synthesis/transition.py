"""
Module 4 Stage 3 — QTM Transition Table Construction & Bijectivity Validation.

Constructs finite transition table T: E(D_fin) -> E(D_fin) and verifies totality, injectivity, and surjectivity.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from src.module1.utm.model import UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module4.foundation.domain import FiniteDomainContract, config_to_key
from src.module4.foundation.encoding import RegisterEncodingSpec, encode_configuration, verify_encoding_injectivity


@dataclass(frozen=True)
class TransitionPair:
    """A single transition mapping pair E(C) -> E(R_P(C))."""
    source_config: RUTMConfiguration
    target_config: RUTMConfiguration
    source_bits: str
    target_bits: str


@dataclass
class TransitionTable:
    """
    Finite transition relation T = { E(C) -> E(R_P(C)) | C in D_fin }.
    
    Guarantees:
    1. Totality: dom(T) == E(D_fin)
    2. Bijectivity: Injective & Surjective mapping on E(D_fin)
    """
    domain_contract: FiniteDomainContract
    encoding_spec: RegisterEncodingSpec
    state_map: Dict[str, int]
    symbol_map: Dict[str, int]
    pairs: List[TransitionPair] = field(default_factory=list)
    forward_mapping: Dict[str, str] = field(default_factory=dict)
    reverse_mapping: Dict[str, str] = field(default_factory=dict)

    @property
    def cardinality(self) -> int:
        return len(self.pairs)


def build_transition_table(
    program: UTMProgram,
    domain_contract: FiniteDomainContract,
    encoding_spec: RegisterEncodingSpec,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
) -> TransitionTable:
    """
    Constructs and verifies the finite transition table T over D_fin.
    
    Rejects synthesis if domain is unclosed, non-finite, or encoding is non-injective.
    """
    # 1. Verify encoding injectivity
    if not verify_encoding_injectivity(domain_contract.domain, encoding_spec, state_map, symbol_map):
        raise ValueError("Synthesis rejected: Configuration encoding E is non-injective (collision detected).")

    # 2. Verify domain closure
    val_res = domain_contract.validate(program)
    if not val_res.valid:
        raise ValueError(f"Synthesis rejected: FiniteDomainContract validation failed. Diagnostics: {val_res.diagnostics}")

    pairs: List[TransitionPair] = []
    forward_mapping: Dict[str, str] = {}
    reverse_mapping: Dict[str, str] = {}

    for source_c in domain_contract.domain:
        # Compute forward step R_P(C)
        target_c = forward_step_rutm(source_c, program)
        source_bits = encode_configuration(source_c, encoding_spec, state_map, symbol_map)
        target_bits = encode_configuration(target_c, encoding_spec, state_map, symbol_map)

        pair = TransitionPair(
            source_config=source_c,
            target_config=target_c,
            source_bits=source_bits,
            target_bits=target_bits,
        )
        pairs.append(pair)

        if source_bits in forward_mapping:
            raise ValueError(f"Transition table collision: duplicate source bitstring {source_bits}.")
        forward_mapping[source_bits] = target_bits

        if target_bits in reverse_mapping:
            # Check bijectivity
            existing_src = reverse_mapping[target_bits]
            if existing_src != source_bits:
                raise ValueError(f"Bijectivity failure: target bitstring {target_bits} mapped from multiple sources ({existing_src}, {source_bits}).")
        reverse_mapping[target_bits] = source_bits

    # 3. Verify totality and surjectivity
    if len(forward_mapping) != domain_contract.cardinality:
        raise ValueError(f"Transition totality failure: expected {domain_contract.cardinality} entries, got {len(forward_mapping)}.")
    if len(reverse_mapping) != domain_contract.cardinality:
        raise ValueError(f"Transition surjectivity failure: reverse mapping cardinality mismatch.")

    return TransitionTable(
        domain_contract=domain_contract,
        encoding_spec=encoding_spec,
        state_map=state_map,
        symbol_map=symbol_map,
        pairs=pairs,
        forward_mapping=forward_mapping,
        reverse_mapping=reverse_mapping,
    )
