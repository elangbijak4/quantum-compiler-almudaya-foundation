"""
Module 6 Stage 2 — Empirical Image Characterizer.

Constructs Img_N(F) and OpImg_N(F), separating structural and semantic operator identities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
import hashlib
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.image.signature import ImageSignature, compute_image_signature
from src.module6.image.collision import CollisionRecord, CollisionAnalyzer


@dataclass(frozen=True)
class EmpiricalImageSummary:
    """
    Summary metrics for an empirical image characterization.
    """
    source_algorithm_count: int
    circuit_image_count: int              # |Img_N(F)|
    operator_image_count: int             # |OpImg_N(F)|
    structural_diversity_ratio: float     # |Img_N(F)| / |A_N|
    operator_diversity_ratio: float       # |OpImg_N(F)| / |A_N|
    unique_operator_classes: Tuple[str, ...]
    signatures: Tuple[ImageSignature, ...]
    collisions: Tuple[CollisionRecord, ...]


class EmpiricalImageCharacterizer:
    """
    Analyzes a collection of classical semantic models A_N and compiled circuits F(A_N).
    """

    @classmethod
    def characterize_image(
        cls,
        models: List[ClassicalSemanticModel],
        circuits: List[QuantumCircuitIR],
    ) -> EmpiricalImageSummary:
        """
        Executes empirical characterization over A_N and F(A_N).
        """
        if len(models) != len(circuits):
            raise ValueError(f"Mismatch between models count ({len(models)}) and circuits count ({len(circuits)})")

        signatures: List[ImageSignature] = []
        for m, c in zip(models, circuits):
            sig = compute_image_signature(m, c)
            signatures.append(sig)

        unique_structural_sigs = set(s.circuit_structural_signature for s in signatures)
        unique_operator_classes = sorted(set(s.operator_equivalence_class_id for s in signatures))

        n_models = len(models)
        n_circuits = len(unique_structural_sigs)
        n_operators = len(unique_operator_classes)

        struct_ratio = (n_circuits / n_models) if n_models > 0 else 0.0
        op_ratio = (n_operators / n_models) if n_models > 0 else 0.0

        collisions = CollisionAnalyzer.analyze_collisions(signatures, models, circuits)

        return EmpiricalImageSummary(
            source_algorithm_count=n_models,
            circuit_image_count=n_circuits,
            operator_image_count=n_operators,
            structural_diversity_ratio=struct_ratio,
            operator_diversity_ratio=op_ratio,
            unique_operator_classes=tuple(unique_operator_classes),
            signatures=tuple(signatures),
            collisions=tuple(collisions),
        )
