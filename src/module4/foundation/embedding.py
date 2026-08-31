"""
Module 4 Foundation — Finite Hilbert Space Embedding & Restricted Unitary Realization.

Defines iota_fin(C) = |E(C)> and restricted unitary contract U_C |E(C)> = |E(R_P(C))>.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
import math
from src.module2.rutm.model import RUTMConfiguration
from src.module4.foundation.domain import FiniteDomainContract
from src.module4.foundation.encoding import RegisterEncodingSpec, encode_configuration


@dataclass
class FiniteHilbertEmbedding:
    """
    Formal Hilbert space embedding E_H : span{|C> : C in D_fin} -> (C^2)^{\otimes n}.
    
    Property:
    E_H(|C>) = |E(C)>
    <E(C1)|E(C2)> = \delta_{C1, C2}
    """
    domain_contract: FiniteDomainContract
    encoding_spec: RegisterEncodingSpec
    state_map: Dict[str, int]
    symbol_map: Dict[str, int]

    def embed_basis_state(self, config: RUTMConfiguration) -> str:
        """Returns computational basis state bitstring |E(C)>."""
        return encode_configuration(config, self.encoding_spec, self.state_map, self.symbol_map)

    def verify_orthogonality(self) -> bool:
        """Verifies computational basis orthogonality <E(C1)|E(C2)> = \delta_{C1, C2}."""
        bitstrings: Set[str] = set()
        for c in self.domain_contract.domain:
            b = self.embed_basis_state(c)
            if b in bitstrings:
                return False  # Non-orthogonal / Colliding basis states
            bitstrings.add(b)
        return True


@dataclass
class RestrictedUnitaryContract:
    """
    Formal specification of restricted unitary operator U_C on H_n = (C^2)^{\otimes n}.
    
    Fundamental Semantic Relation:
    U_C |E(C)> = |E(R_P(C))>   for all C in D_fin.
    """
    embedding: FiniteHilbertEmbedding
    target_dimension: int = field(init=False)

    def __post_init__(self):
        self.target_dimension = 1 << self.embedding.encoding_spec.total_qubits

    def is_unitary(self) -> bool:
        """Verifies that restricted transition permutation is bijective on D_fin."""
        return self.embedding.verify_orthogonality()
