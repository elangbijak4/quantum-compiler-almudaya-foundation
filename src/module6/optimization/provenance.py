"""
Module 6 Stage 8 — Optimization Provenance Generator.

Generates deterministic provenance metadata for optimization cost reports.
"""

from typing import Dict, Any, Tuple
import hashlib
import json


class OptimizationProvenanceGenerator:
    """
    Generates auditable, deterministic provenance records for Stage 8 optimization.
    """

    @classmethod
    def generate_provenance(
        cls,
        algorithm_id: str,
        evolution_stage: str,
        effective_vocabulary: Tuple[str, ...],
        initial_cost: int,
        optimized_cost: int,
        context_hash: str = "",
        semantic_verified: bool = True,
    ) -> Dict[str, Any]:
        """
        Builds deterministic provenance metadata dictionary.
        """
        raw_id = (
            f"PROV_OPT_{algorithm_id}_{evolution_stage}_"
            f"{','.join(effective_vocabulary)}_{initial_cost}_{optimized_cost}_{context_hash}_{semantic_verified}"
        )
        p_hash = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

        return {
            "optimization_provenance_id": p_hash,
            "algorithm_id": algorithm_id,
            "evolution_stage": evolution_stage,
            "effective_vocabulary": list(effective_vocabulary),
            "initial_gate_count": initial_cost,
            "optimized_gate_count": optimized_cost,
            "context_hash": context_hash,
            "semantic_verified": semantic_verified,
            "stage_id": "Stage 8 Optimization Engine",
            "compiler_version": "0.6.0-stage8",
        }
