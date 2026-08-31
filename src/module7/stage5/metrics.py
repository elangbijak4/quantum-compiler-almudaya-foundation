"""
Module 7 Stage 5 — Statistical Distance Metrics Implementation.

Provides HellingerDistanceCalculator and KSDistanceCalculator for discrete probability
distribution analysis over canonical joint support spaces.
"""

from typing import Dict, Set, Tuple, Optional
import math


class HellingerDistanceCalculator:
    """
    Computes exact Hellinger Distance between two discrete probability distributions.
    
    Formula:
      H(P, Q) = (1 / sqrt(2)) * sqrt( sum_{x in P union Q} (sqrt(P(x)) - sqrt(Q(x)))^2 )
      
    Invariants:
    1. Output range is strictly in [0.0, 1.0].
    2. Zero-probability outcomes in sparse support are handled cleanly without division by zero.
    3. Rejects distributions containing NaN, infinity, or negative probabilities.
    """

    def calculate(
        self,
        p_dist: Dict[str, float],
        q_dist: Dict[str, float],
        numerical_tolerance: float = 1e-6,
    ) -> float:
        """Calculates Hellinger distance between distributions p_dist and q_dist."""
        self._validate_distribution(p_dist, numerical_tolerance)
        self._validate_distribution(q_dist, numerical_tolerance)

        joint_keys: Set[str] = set(p_dist.keys()).union(set(q_dist.keys()))
        sum_sq_diff = 0.0

        for k in joint_keys:
            p_val = p_dist.get(k, 0.0)
            q_val = q_dist.get(k, 0.0)
            diff = math.sqrt(p_val) - math.sqrt(q_val)
            sum_sq_diff += diff * diff

        h_dist = (1.0 / math.sqrt(2.0)) * math.sqrt(sum_sq_diff)
        return min(max(h_dist, 0.0), 1.0)

    def _validate_distribution(self, dist: Dict[str, float], tolerance: float) -> None:
        if not dist:
            raise ValueError("Distribution cannot be empty.")

        total_prob = 0.0
        for val in dist.values():
            if math.isnan(val) or math.isinf(val):
                raise ValueError("Distribution contains invalid numerical value (NaN or infinity).")
            if val < 0.0:
                raise ValueError("Distribution contains negative probability.")
            total_prob += val

        if abs(total_prob - 1.0) > tolerance:
            raise ValueError(f"Distribution normalization drift ({total_prob}) exceeds tolerance ({tolerance}).")


class KSDistanceCalculator:
    """
    Computes Kolmogorov-Smirnov (KS) Distance over discrete bitstring distributions.
    
    Formula:
      D_KS = max_x | F_P(x) - F_Q(x) |
    where F_P and F_Q are Cumulative Distribution Functions over lexicographically ordered keys.
    """

    def calculate(
        self,
        p_dist: Dict[str, float],
        q_dist: Dict[str, float],
        numerical_tolerance: float = 1e-6,
    ) -> float:
        """Calculates discrete KS distance between distributions p_dist and q_dist."""
        joint_keys = sorted(list(set(p_dist.keys()).union(set(q_dist.keys()))))
        if not joint_keys:
            return 0.0

        cdf_p = 0.0
        cdf_q = 0.0
        max_diff = 0.0

        for k in joint_keys:
            cdf_p += p_dist.get(k, 0.0)
            cdf_q += q_dist.get(k, 0.0)
            diff = abs(cdf_p - cdf_q)
            if diff > max_diff:
                max_diff = diff

        return min(max(max_diff, 0.0), 1.0)
