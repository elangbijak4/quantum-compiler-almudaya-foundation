"""
Module 6 Stage 3 — Classical Algorithm Identity Model.

Defines immutable identity representation for classical algorithms A in A_C.
Distinguishes syntactic identity from classical semantic identity A1 ==_syntactic A2 vs A1 \equiv_C A2.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
import hashlib
from src.module1.utm.model import UTMProgram
from src.module6.classical.semantic import ClassicalSemanticModel


@dataclass(frozen=True)
class ClassicalAlgorithmIdentity:
    """
    Immutable identity descriptor for a classical algorithm A in A_C.
    """
    algorithm_id: str
    semantic_model_id: str
    program_hash: str
    domain_id: str
    transition_hash: str
    provenance: Dict[str, str] = field(default_factory=dict)

    def is_syntactically_identical(self, other: "ClassicalAlgorithmIdentity") -> bool:
        """Checks syntactic identity (exact program hash and domain ID equality)."""
        return self.program_hash == other.program_hash and self.domain_id == other.domain_id


def create_classical_algorithm_identity(
    model: ClassicalSemanticModel,
    program: UTMProgram,
) -> ClassicalAlgorithmIdentity:
    """
    Creates a deterministic ClassicalAlgorithmIdentity from a model and UTM program.
    """
    prog_raw = f"{sorted(program.states)}|{sorted(program.alphabet)}|{program.initial_state}|{program.halt_state}"
    prog_hash = hashlib.sha256(prog_raw.encode("utf-8")).hexdigest()
    sem_id = model.compute_deterministic_id()

    # Compute transition table hash
    t_rows: list[str] = []
    for src_b, tgt_b in sorted(model.transition_table.items()):
        t_rows.append(f"{src_b}->{tgt_b}")
    raw_t = "|".join(t_rows)
    t_hash = hashlib.sha256(raw_t.encode("utf-8")).hexdigest()

    # Compute domain ID
    d_rows = sorted(str(c) for c in model.domain_contract.domain)
    raw_d = "|".join(d_rows)
    d_id = f"DOM_{hashlib.sha256(raw_d.encode('utf-8')).hexdigest()[:16]}"

    prov = {
        "module": "module6",
        "stage": "stage3",
        "algorithm_id": model.algorithm_id,
        "program_hash": prog_hash,
    }

    return ClassicalAlgorithmIdentity(
        algorithm_id=model.algorithm_id,
        semantic_model_id=sem_id,
        program_hash=prog_hash,
        domain_id=d_id,
        transition_hash=t_hash,
        provenance=prov,
    )
