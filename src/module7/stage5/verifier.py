"""
Module 7 Stage 5 — Production Statistical Verification Engine.

Provides StatisticalVerificationEngine implementing StatisticalVerifierProtocol for evaluating
observed execution results against reference distributions under governed policies.
"""

from typing import Dict, Any, Optional
import uuid

from src.module7.stage4.model import ProviderNeutralExecutionResult
from src.module7.stage5.model import (
    StatisticalVerificationDecision,
    StatisticalVerificationPolicy,
    StatisticalVerificationRecord,
)
from src.module7.stage5.interfaces import StatisticalVerifierProtocol
from src.module7.stage5.metrics import HellingerDistanceCalculator, KSDistanceCalculator


class StatisticalVerificationEngine(StatisticalVerifierProtocol):
    """
    Module 7 Stage 5 Production Engine.
    
    Coordinates distribution normalization, distance calculation, policy threshold evaluation,
    and StatisticalVerificationRecord generation.
    """

    def __init__(self) -> None:
        self.hellinger_calc = HellingerDistanceCalculator()
        self.ks_calc = KSDistanceCalculator()

    def verify_result(
        self,
        observed_result: ProviderNeutralExecutionResult,
        reference_distribution: Dict[str, float],
        reference_id: str,
        policy: StatisticalVerificationPolicy,
    ) -> StatisticalVerificationRecord:
        """Evaluates statistical consistency of observed result against reference distribution."""
        verification_id = f"VERIF_{uuid.uuid4().hex[:8].upper()}"

        # 1. Shot Count Minimum Check
        if observed_result.shots < policy.min_shots:
            return StatisticalVerificationRecord(
                verification_id=verification_id,
                execution_id=observed_result.job_id,
                native_circuit_hash=observed_result.native_circuit_hash,
                reference_id=reference_id,
                observed_result_hash=observed_result.result_hash,
                decision=StatisticalVerificationDecision.INCONCLUSIVE,
                hellinger_distance=None,
                ks_distance=None,
                observed_shots=observed_result.shots,
                policy_hash=policy.policy_hash,
                provenance={
                    "failure_reason": f"INSUFFICIENT_SHOTS: Observed shots ({observed_result.shots}) < min_shots ({policy.min_shots}).",
                    "policy_id": policy.policy_id,
                },
            )

        # 2. Normalize Observed Counts to Probability Distribution
        total_counts = sum(observed_result.measurement_counts.values())
        if total_counts == 0 or not reference_distribution:
            return StatisticalVerificationRecord(
                verification_id=verification_id,
                execution_id=observed_result.job_id,
                native_circuit_hash=observed_result.native_circuit_hash,
                reference_id=reference_id,
                observed_result_hash=observed_result.result_hash,
                decision=StatisticalVerificationDecision.INCONCLUSIVE,
                hellinger_distance=None,
                ks_distance=None,
                observed_shots=observed_result.shots,
                policy_hash=policy.policy_hash,
                provenance={
                    "failure_reason": "EMPTY_DISTRIBUTION: Measurement counts or reference distribution is empty.",
                    "policy_id": policy.policy_id,
                },
            )

        p_observed = {k: v / total_counts for k, v in observed_result.measurement_counts.items()}

        # 3. Calculate Hellinger and KS Distance Metrics
        try:
            h_dist = self.hellinger_calc.calculate(
                p_observed, reference_distribution, policy.numerical_tolerance
            )
            ks_dist = self.ks_calc.calculate(
                p_observed, reference_distribution, policy.numerical_tolerance
            )
        except Exception as err:
            return StatisticalVerificationRecord(
                verification_id=verification_id,
                execution_id=observed_result.job_id,
                native_circuit_hash=observed_result.native_circuit_hash,
                reference_id=reference_id,
                observed_result_hash=observed_result.result_hash,
                decision=StatisticalVerificationDecision.INCONCLUSIVE,
                hellinger_distance=None,
                ks_distance=None,
                observed_shots=observed_result.shots,
                policy_hash=policy.policy_hash,
                provenance={
                    "failure_reason": f"NUMERICAL_ERROR: {str(err)}",
                    "policy_id": policy.policy_id,
                },
            )

        # 4. Evaluate Threshold Policy
        if h_dist <= policy.hellinger_threshold and ks_dist <= policy.ks_threshold:
            decision = StatisticalVerificationDecision.VERIFIED
        else:
            decision = StatisticalVerificationDecision.REJECTED

        return StatisticalVerificationRecord(
            verification_id=verification_id,
            execution_id=observed_result.job_id,
            native_circuit_hash=observed_result.native_circuit_hash,
            reference_id=reference_id,
            observed_result_hash=observed_result.result_hash,
            decision=decision,
            hellinger_distance=h_dist,
            ks_distance=ks_dist,
            observed_shots=observed_result.shots,
            policy_hash=policy.policy_hash,
            provenance={
                "provider_id": observed_result.provider_id,
                "backend_id": observed_result.backend_id,
                "provider_job_id": observed_result.provider_job_id,
                "policy_id": policy.policy_id,
                "policy_version": policy.policy_version,
            },
        )
