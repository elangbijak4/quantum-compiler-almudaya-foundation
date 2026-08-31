"""
Module 7 Stage 3 — Deterministic Shot Sampler Engine.

Provides DeterministicShotSampler for computational basis bitstring shot sampling
given statevector probability distributions and deterministic PRNG seeding.
"""

import random
from typing import Dict, List, Tuple


class DeterministicShotSampler:
    """
    Deterministic PRNG Shot Sampler.
    
    Given exact probability distribution P(k), samples N_shots using a seeded PRNG.
    """

    def __init__(self, seed_prng: int = 42) -> None:
        self.seed_prng = seed_prng
        self.rng = random.Random(seed_prng)

    def sample_shots(self, probabilities: Dict[str, float], shots: int) -> Tuple[Dict[str, int], Dict[str, float]]:
        """
        Samples computational basis bitstring occurrences.
        
        Returns:
            (measurement_counts, measurement_distribution)
        """
        if shots <= 0 or shots > 1000000:
            raise ValueError(f"EXECUTION_RESOURCE_EXHAUSTED: Invalid shot count {shots} (must be 1..1000000).")

        bitstrings = sorted(probabilities.keys())
        cumulative_weights: List[float] = []
        cum_sum = 0.0
        for b in bitstrings:
            cum_sum += probabilities[b]
            cumulative_weights.append(cum_sum)

        # Normalize cumulative weights to 1.0
        if cumulative_weights and cumulative_weights[-1] > 0:
            total_w = cumulative_weights[-1]
            cumulative_weights = [w / total_w for w in cumulative_weights]

        counts: Dict[str, int] = {b: 0 for b in bitstrings}

        for _ in range(shots):
            r = self.rng.random()
            # Binary search or linear search for interval
            idx = 0
            for i, w in enumerate(cumulative_weights):
                if r <= w:
                    idx = i
                    break
            counts[bitstrings[idx]] += 1

        dist: Dict[str, float] = {b: c / float(shots) for b, c in counts.items()}
        return counts, dist
