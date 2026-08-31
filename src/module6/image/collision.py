"""
Module 6 Stage 2 — Collision Analyzer.

Investigates classical semantic collisions, syntactic circuit collisions, and semantic circuit collisions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Set
import hashlib
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.image.signature import ImageSignature


class CollisionType(str, Enum):
    """Classification of empirical compiler collisions."""
    CLASSICAL_SEMANTIC_COLLISION = "CLASSICAL_SEMANTIC_COLLISION"  # A1 !=_C A2 but F(A1) ==_Q F(A2)
    SYNTACTIC_CIRCUIT_COLLISION = "SYNTACTIC_CIRCUIT_COLLISION"    # F(A1) == F(A2)
    SEMANTIC_CIRCUIT_COLLISION = "SEMANTIC_CIRCUIT_COLLISION"      # F(A1) != F(A2) but U(F(A1)) ==_Q U(F(A2))


@dataclass(frozen=True)
class CollisionRecord:
    """
    Immutable record of an observed collision.
    """
    collision_id: str
    collision_type: CollisionType
    algorithm_id_1: str
    algorithm_id_2: str
    circuit_id_1: str
    circuit_id_2: str
    operator_hash_1: str
    operator_hash_2: str
    details: str


class CollisionAnalyzer:
    """
    Analyzes collision pairs across a collection of classical semantic models and compiled circuits.
    """

    @classmethod
    def analyze_collisions(
        cls,
        signatures: List[ImageSignature],
        models: List[ClassicalSemanticModel],
        circuits: List[QuantumCircuitIR],
    ) -> List[CollisionRecord]:
        """
        Detects collisions across all pairs of analyzed algorithms.
        """
        collisions: List[CollisionRecord] = []
        n = len(signatures)

        model_dict = {m.algorithm_id: m for m in models}
        circuit_dict = {c.circuit_id: c for c in circuits}

        for i in range(n):
            for j in range(i + 1, n):
                sig1 = signatures[i]
                sig2 = signatures[j]

                m1 = model_dict[sig1.algorithm_id]
                m2 = model_dict[sig2.algorithm_id]

                c1 = circuit_dict[sig1.circuit_id]
                c2 = circuit_dict[sig2.circuit_id]

                # Check Classical Equivalence
                classically_equal = (m1.compute_deterministic_id() == m2.compute_deterministic_id())

                # Check Syntactic Circuit Equivalence
                syntactically_equal = (sig1.circuit_structural_signature == sig2.circuit_structural_signature)

                # Check Operator Semantic Equivalence
                operator_equal = (sig1.operator_hash == sig2.operator_hash)

                if operator_equal:
                    if not classically_equal:
                        raw = f"{sig1.algorithm_id}|{sig2.algorithm_id}|CLASSICAL_SEMANTIC"
                        cid = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
                        collisions.append(
                            CollisionRecord(
                                collision_id=cid,
                                collision_type=CollisionType.CLASSICAL_SEMANTIC_COLLISION,
                                algorithm_id_1=sig1.algorithm_id,
                                algorithm_id_2=sig2.algorithm_id,
                                circuit_id_1=sig1.circuit_id,
                                circuit_id_2=sig2.circuit_id,
                                operator_hash_1=sig1.operator_hash,
                                operator_hash_2=sig2.operator_hash,
                                details="Classical models differ semantically but yield operator-equivalent logical circuits.",
                            )
                        )
                    elif not syntactically_equal:
                        raw = f"{sig1.algorithm_id}|{sig2.algorithm_id}|SEMANTIC_CIRCUIT"
                        cid = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
                        collisions.append(
                            CollisionRecord(
                                collision_id=cid,
                                collision_type=CollisionType.SEMANTIC_CIRCUIT_COLLISION,
                                algorithm_id_1=sig1.algorithm_id,
                                algorithm_id_2=sig2.algorithm_id,
                                circuit_id_1=sig1.circuit_id,
                                circuit_id_2=sig2.circuit_id,
                                operator_hash_1=sig1.operator_hash,
                                operator_hash_2=sig2.operator_hash,
                                details="Circuits differ structurally but yield operator-equivalent unitaries.",
                            )
                        )

                if syntactically_equal and sig1.algorithm_id != sig2.algorithm_id:
                    raw = f"{sig1.algorithm_id}|{sig2.algorithm_id}|SYNTACTIC_CIRCUIT"
                    cid = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
                    collisions.append(
                        CollisionRecord(
                            collision_id=cid,
                            collision_type=CollisionType.SYNTACTIC_CIRCUIT_COLLISION,
                            algorithm_id_1=sig1.algorithm_id,
                            algorithm_id_2=sig2.algorithm_id,
                            circuit_id_1=sig1.circuit_id,
                            circuit_id_2=sig2.circuit_id,
                            operator_hash_1=sig1.operator_hash,
                            operator_hash_2=sig2.operator_hash,
                            details="Distinct algorithm IDs produced identical canonical circuit structures.",
                        )
                    )

        return collisions
