"""
Module 6 Stage 1 — Classical Transition Extractor & Validator.

Extracts finite-domain transition tables R_P : D_fin -> D_fin from Module 1/2 semantics,
verifying totality, determinism, domain closure, and bijectivity (reversibility).
"""

from typing import Dict, List, Set, Tuple, Optional
import hashlib
from src.module1.utm.model import UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module4.foundation.domain import FiniteDomainContract
from src.module4.foundation.encoding import (
    RegisterEncodingSpec,
    compute_register_encoding_spec,
    encode_configuration,
    verify_encoding_injectivity,
)
from src.module4.synthesis.transition import build_transition_table
from src.module6.classical.semantic import ClassicalSemanticModel


def build_classical_semantic_model(
    program: UTMProgram,
    domain_contract: FiniteDomainContract,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
    algorithm_id: str = "default_alg",
) -> ClassicalSemanticModel:
    """
    Constructs an immutable ClassicalSemanticModel for A in A_C.
    
    Verifies:
    1. Domain contract validity.
    2. Encoding injectivity.
    3. Totality & determinism of R_P : D_fin -> D_fin.
    4. Bijectivity (reversibility) over D_fin.
    """
    # 1. Validate Domain Contract
    domain_val = domain_contract.validate(program)
    if not domain_val.valid:
        raise ValueError(f"Domain contract validation failed: {domain_val.diagnostics}")

    # 2. Compute Encoding Spec using exact signature: compute_register_encoding_spec(domain, all_states, alphabet)
    encoding_spec = compute_register_encoding_spec(
        domain=domain_contract.domain,
        all_states=set(program.states),
        alphabet=set(program.alphabet),
    )

    # 3. Verify Encoding Injectivity
    injective = verify_encoding_injectivity(
        domain_contract.domain, encoding_spec, state_map, symbol_map
    )
    if not injective:
        raise ValueError("Configuration encoding E is non-injective (collision detected).")

    # 4. Build Transition Table
    table_obj = build_transition_table(
        program, domain_contract, encoding_spec, state_map, symbol_map
    )
    transition_table = table_obj.forward_mapping

    # 5. Verify Totality and Bijectivity (Reversibility)
    mapped_inputs = set(transition_table.keys())
    mapped_outputs = set(transition_table.values())

    if len(mapped_inputs) != len(domain_contract.domain):
        raise ValueError(f"Transition relation is non-total over D_fin ({len(mapped_inputs)} != {len(domain_contract.domain)}).")

    if len(mapped_outputs) != len(mapped_inputs):
        raise ValueError("Transition relation is non-bijective (reversibility violation).")

    # 6. Identify Halting and Error Configurations
    halting_configs: Set[str] = set()
    error_configs: Set[str] = set()

    for config in domain_contract.domain:
        enc_bits = encode_configuration(config, encoding_spec, state_map, symbol_map)
        if config.halted or config.current_state == program.halt_state:
            halting_configs.add(enc_bits)
        if config.current_state not in program.states:
            error_configs.add(enc_bits)

    # 7. Compute Source Program Hash
    raw_hash = hashlib.sha256(str(program).encode("utf-8")).hexdigest()

    return ClassicalSemanticModel(
        algorithm_id=algorithm_id,
        source_program_hash=raw_hash,
        domain_contract=domain_contract,
        encoding_spec=encoding_spec,
        state_map=state_map,
        symbol_map=symbol_map,
        transition_table=transition_table,
        initial_config=domain_contract.initial_configuration,
        halting_configs=halting_configs,
        error_configs=error_configs,
    )
