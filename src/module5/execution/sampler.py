"""
Module 5 Stage 5 Step 2 — Probability Extraction & Seeded Shot Sampler.

Implements computational-basis probability extraction and local deterministic PRNG shot sampling.
"""

from typing import Dict, List, Tuple, Optional
import math
import random
from src.module5.execution.state import QuantumState
from src.module5.execution.model import MeasurementResult, EPSILON


class ShotSampler:
    """
    Computes analytical probabilities and performs local seeded pseudo-random shot sampling.
    Does NOT mutate global random state. Uses big-endian bitstring conventions.
    """

    @classmethod
    def extract_probabilities(cls, state: QuantumState) -> Dict[str, float]:
        """
        Extracts computational-basis probability distribution P(x) = |alpha_x|^2.
        Analytical probabilities are strictly deterministic and independent of random seed.
        """
        probs = state.probabilities()
        sum_p = sum(probs.values())

        if abs(sum_p - 1.0) >= EPSILON:
            raise ValueError(f"Analytical probability distribution sum failure: sum P(x) = {sum_p:.10f}, expected 1.0 +/- {EPSILON}.")

        # Return sorted dictionary by bitstring key
        sorted_keys = sorted(probs.keys())
        return {k: probs[k] for k in sorted_keys}

    @classmethod
    def sample_shots(
        cls,
        state: QuantumState,
        shots: int,
        seed: Optional[int] = None,
    ) -> MeasurementResult:
        """
        Performs seeded computational-basis shot sampling.
        
        Guarantees:
        1. Local PRNG instance (random.Random(seed)) — zero global RNG mutation.
        2. Exact reproducibility: Execute(C, seed=S, N) == Execute(C, seed=S, N).
        3. Shot count invariant: len(shot_sequence) == shots and sum(counts) == shots.
        4. Seed independence for analytical probabilities: P_s1(x) == P_s2(x).
        """
        if shots <= 0:
            raise ValueError(f"Shot count must be strictly positive (> 0), got {shots}.")

        probabilities = cls.extract_probabilities(state)

        # Initialize local PRNG instance
        prng = random.Random(seed) if seed is not None else random.Random()

        bitstrings = list(probabilities.keys())
        weights = [probabilities[b] for b in bitstrings]

        # Draw shots using local PRNG
        shot_sequence: List[str] = prng.choices(bitstrings, weights=weights, k=shots)

        # Aggregate counts
        counts: Dict[str, int] = {}
        for b in shot_sequence:
            counts[b] = counts.get(b, 0) + 1

        # Sort counts keys deterministically
        sorted_counts = {k: counts[k] for k in sorted(counts.keys())}

        return MeasurementResult(
            probabilities=probabilities,
            counts=sorted_counts,
            shot_sequence=shot_sequence,
            shot_count=shots,
            seed=seed,
        )
