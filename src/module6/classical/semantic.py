"""
Module 6 Stage 1 — Classical Semantic Model.

Defines the immutable classical algorithm semantic model representation A_C = A_semantic
over a finite transition system (D_fin, R_P).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import hashlib
from src.module2.rutm.model import RUTMConfiguration
from src.module4.foundation.domain import FiniteDomainContract
from src.module4.foundation.encoding import RegisterEncodingSpec


@dataclass(frozen=True)
class ClassicalSemanticModel:
    """
    Immutable representation of a classical semantic algorithm A in A_C = A_semantic.
    
    Models a finite-domain transition system (D_fin, R_P) with:
    - D_fin subset C_R (|D_fin| < infinity)
    - R_P : D_fin -> D_fin
    """
    algorithm_id: str
    source_program_hash: str
    domain_contract: FiniteDomainContract
    encoding_spec: RegisterEncodingSpec
    state_map: Dict[str, int]
    symbol_map: Dict[str, int]
    transition_table: Dict[str, str]  # E(C) -> E(R_P(C))
    initial_config: Optional[RUTMConfiguration] = None
    halting_configs: Set[str] = field(default_factory=set)  # set of encoded bitstrings
    error_configs: Set[str] = field(default_factory=set)    # set of encoded bitstrings

    def compute_deterministic_id(self) -> str:
        """Computes deterministic identity hash of the classical semantic model."""
        content = [
            f"ALG:{self.algorithm_id}",
            f"HASH:{self.source_program_hash}",
            f"SIZE:{len(self.domain_contract.domain)}",
        ]
        for k in sorted(self.transition_table.keys()):
            content.append(f"{k}->{self.transition_table[k]}")
        raw = "|".join(content).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


def create_sample_adder_model() -> ClassicalSemanticModel:
    """Helper function creating a valid sample ClassicalSemanticModel for testing."""
    from src.module6.families.generators import AlgorithmFamilyGenerator
    family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
    return list(family.models)[0]



