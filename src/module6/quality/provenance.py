"""
Module 6 Stage 9 — Quality Provenance Generator.

Generates auditable, deterministic provenance records for Stage 9 quality analysis and comparisons.
Distinguishes FACT, DERIVED_METRIC, POLICY, and USER_PREFERENCE.
"""

from typing import Dict, Any, List, Optional
import hashlib


class QualityProvenanceGenerator:
    """
    Generates auditable, deterministic provenance records for Stage 9.
    """

    @classmethod
    def generate_provenance(
        cls,
        algorithm_id: str,
        evolution_stage: str,
        session_id: str,
        classification: str,
        total_gates: int,
        original_circuit_hash: str = "",
        optimized_circuit_hash: str = "",
        effective_vocabulary_hash: str = "",
        stage8_report_hash: str = "",
        stage4_verification_status: str = "VERIFIED",
        active_objectives: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Builds comprehensive provenance dictionary with SHA-256 digest."""
        objs = active_objectives if active_objectives is not None else ["total_gate_count", "circuit_depth", "total_qubits"]

        raw_str = (
            f"{algorithm_id}:{evolution_stage}:{session_id}:{classification}:{total_gates}:"
            f"{original_circuit_hash}:{optimized_circuit_hash}:{effective_vocabulary_hash}:"
            f"{stage8_report_hash}:{stage4_verification_status}:{','.join(objs)}"
        )
        p_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        return {
            "quality_provenance_id": p_hash[:16],
            "full_provenance_hash": p_hash,
            "facts": {
                "algorithm_id": algorithm_id,
                "evolution_stage": evolution_stage,
                "session_id": session_id,
                "original_circuit_hash": original_circuit_hash,
                "optimized_circuit_hash": optimized_circuit_hash,
                "effective_vocabulary_hash": effective_vocabulary_hash,
                "stage8_report_hash": stage8_report_hash,
                "stage4_verification_status": stage4_verification_status,
            },
            "derived_metrics": {
                "total_gates": total_gates,
                "classification": classification,
            },
            "policy": {
                "active_objectives": objs,
                "stage_id": "Stage 9 Engine Implementation",
            },
            "user_preference": {
                "session_id": session_id,
            },
        }
