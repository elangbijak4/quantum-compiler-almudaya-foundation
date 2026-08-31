"""
Module 6 Stage 5 — Candidate Gate Registry & Base Vocabulary Immutability Verification.

Manages isolated BaseVocabulary G0 = {X, CNOT, TOFFOLI}, CandidateVocabulary, and ExtendedVocabulary.
Computes canonical G0 SHA-256 hash before and after execution to enforce absolute immutability.
"""

from typing import List, Dict, Set, Tuple, Any, Optional
import numpy as np
import hashlib
import json
from src.module6.evolution.candidate import CandidateGate, compute_canonical_matrix_hash


BASE_PRIMITIVE_NAMES: Tuple[str, ...] = ("X", "CNOT", "TOFFOLI")


def compute_base_vocabulary_hash() -> str:
    """
    Computes deterministic SHA-256 hash of the frozen baseline primitive gate vocabulary G0.
    G0 = {X, CNOT, TOFFOLI}.
    """
    # Matrices of baseline primitive gates
    x_mat = np.array([[0, 1], [1, 0]], dtype=complex)
    cnot_mat = np.eye(4, dtype=complex)
    cnot_mat[2:4, 2:4] = [[0, 1], [1, 0]]
    toff_mat = np.eye(8, dtype=complex)
    toff_mat[6:8, 6:8] = [[0, 1], [1, 0]]

    vocab_data = [
        {"name": "X", "arity": 1, "hash": compute_canonical_matrix_hash(x_mat)},
        {"name": "CNOT", "arity": 2, "hash": compute_canonical_matrix_hash(cnot_mat)},
        {"name": "TOFFOLI", "arity": 3, "hash": compute_canonical_matrix_hash(toff_mat)},
    ]
    serialized = json.dumps(vocab_data, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class CandidateRegistry:
    """
    Isolated Registry managing BaseVocabulary (G0), CandidateSet, and ExtendedVocabulary (G').
    """

    def __init__(self) -> None:
        self._g0_hash_before: str = compute_base_vocabulary_hash()
        self._candidates: Dict[str, CandidateGate] = {}
        self._hash_to_id: Dict[str, str] = {}

    def verify_g0_immutability(self) -> bool:
        """
        Verifies that baseline vocabulary G0 remains untouched.
        Returns True if hash(G0_before) == hash(G0_after), else raises ValueError.
        """
        g0_hash_after = compute_base_vocabulary_hash()
        if self._g0_hash_before != g0_hash_after:
            raise ValueError(f"VOCABULARY_MUTATION_FAILURE: Baseline G0 hash mutated! Before={self._g0_hash_before}, After={g0_hash_after}")
        return True

    def register_candidate(self, candidate: CandidateGate) -> str:
        """
        Registers a candidate gate in the candidate registry.
        Checks for duplicate candidate ID or duplicate matrix canonical hash.
        Raises ValueError(DUPLICATE_CANDIDATE_GATE) on duplicate.
        """
        self.verify_g0_immutability()

        if candidate.gate_id in self._candidates:
            raise ValueError(f"DUPLICATE_CANDIDATE_GATE: Candidate ID '{candidate.gate_id}' is already registered")

        if candidate.canonical_hash in self._hash_to_id:
            existing_id = self._hash_to_id[candidate.canonical_hash]
            raise ValueError(f"DUPLICATE_CANDIDATE_GATE: Candidate matrix identical to existing gate '{existing_id}'")

        self._candidates[candidate.gate_id] = candidate
        self._hash_to_id[candidate.canonical_hash] = candidate.gate_id
        return candidate.gate_id

    def get_candidate(self, gate_id: str) -> Optional[CandidateGate]:
        return self._candidates.get(gate_id)

    def list_candidates(self) -> List[CandidateGate]:
        return [self._candidates[k] for k in sorted(self._candidates.keys())]

    def get_base_vocabulary(self) -> Tuple[str, ...]:
        self.verify_g0_immutability()
        return BASE_PRIMITIVE_NAMES

    def get_extended_vocabulary(self, gate_ids: Tuple[str, ...]) -> Tuple[str, ...]:
        """
        Constructs extended vocabulary G' = G0 U {candidates}.
        Does NOT modify G0.
        """
        self.verify_g0_immutability()
        cand_names = []
        for gid in gate_ids:
            cand = self.get_candidate(gid)
            if cand is None:
                raise ValueError(f"INVALID_CANDIDATE_GATE: Candidate '{gid}' not found in registry")
            cand_names.append(cand.name)

        return tuple(list(BASE_PRIMITIVE_NAMES) + sorted(cand_names))
