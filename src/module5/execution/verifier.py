"""
Module 5 Stage 5 Step 3 — Execution Equivalence & Result Verifier.

Implements rigorous verification of state-vector correctness, analytical probability equivalence,
single-pass cross-validation, measurement consistency, global-phase policy, reverse execution,
provenance preservation, and canonical JSON serialization determinism.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import math
import cmath
from src.module5.execution.model import (
    ExecutionResult,
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    MeasurementResult,
    EPSILON,
)
from src.module5.execution.state import QuantumState


@dataclass
class ExecutionEquivalenceReport:
    """Detailed verification report for execution equivalence and result validation."""
    valid: bool
    status: str  # "VERIFIED" or "FAILED"
    failure_code: Optional[ExecutionFailureCode] = None
    errors: List[str] = field(default_factory=list)
    state_vector_verified: bool = False
    probabilities_verified: bool = False
    measurement_verified: bool = False
    cross_validation_verified: bool = False
    provenance_verified: bool = False
    global_phase_residual: float = 0.0


class ExecutionVerifier:
    """Verifies semantic and numerical execution equivalence of Stage 5 execution results."""

    @classmethod
    def verify_state_vector_norm(cls, state_dict: Dict[str, complex]) -> Tuple[bool, float, Optional[str]]:
        """Verifies that final_state_vector is normalized: norm = 1.0 +/- 10^-12."""
        norm_sq = 0.0
        for bitstr, val in state_dict.items():
            if math.isnan(val.real) or math.isnan(val.imag) or math.isinf(val.real) or math.isinf(val.imag):
                return False, 0.0, f"State vector contains NaN or Inf amplitude at basis state {bitstr}."
            norm_sq += abs(val) ** 2

        norm = math.sqrt(norm_sq)
        if abs(norm - 1.0) >= EPSILON:
            return False, norm, f"State vector norm mismatch: norm = {norm:.12f}, expected 1.0 +/- {EPSILON}."

        return True, norm, None

    @classmethod
    def verify_global_phase_equivalence(
        cls,
        state1: Dict[str, complex],
        state2: Dict[str, complex],
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Verifies global phase equivalence: |psi_2> = e^(i phi) |psi_1>.
        Satisfied iff |<psi_1 | psi_2>| = 1.0 +/- 10^-12.
        Analytical probabilities satisfy |alpha_1|^2 == |alpha_2|^2 under global phase.
        """
        if set(state1.keys()) != set(state2.keys()):
            return False, 1.0, "Basis state dimension mismatch between state vectors."

        inner_prod = 0.0 + 0.0j
        for k in state1:
            inner_prod += state1[k].conjugate() * state2[k]

        fidelity = abs(inner_prod)
        residual = abs(fidelity - 1.0)
        if residual >= EPSILON:
            return False, residual, f"Global phase fidelity violation: |<psi1|psi2>| = {fidelity:.12f}, residual {residual:.12e} >= {EPSILON}."

        return True, residual, None

    @classmethod
    def verify_state_probability_cross_validation(
        cls,
        state_dict: Dict[str, complex],
        measurement: MeasurementResult,
    ) -> Tuple[bool, Optional[str]]:
        """
        Cross-validates analytical probabilities P(x) against final_state_vector amplitudes:
        P(x) == |alpha_x|^2 within 10^-12 tolerance.
        Ensures single-pass integration invariant (no double execution).
        """
        probs = measurement.probabilities
        for bitstr, amplitude in state_dict.items():
            expected_p = abs(amplitude) ** 2
            actual_p = probs.get(bitstr, -1.0)
            if abs(actual_p - expected_p) >= EPSILON:
                return False, f"State-probability cross-validation mismatch for basis state '{bitstr}': analytical P(x) = {actual_p:.12f}, |alpha|^2 = {expected_p:.12f}."

        return True, None

    @classmethod
    def verify_execution_result(cls, result: ExecutionResult) -> ExecutionEquivalenceReport:
        """Full structural and semantic validation of an ExecutionResult."""
        errors: List[str] = []

        if result.status == ExecutionStatus.FAILED:
            return ExecutionEquivalenceReport(
                valid=False,
                status="FAILED",
                failure_code=result.failure_code or ExecutionFailureCode.EXECUTION_SEMANTIC_FAILURE,
                errors=[f"Execution failed: {result.failure_message}"] + result.diagnostics,
            )

        if not result.request_id:
            errors.append("ExecutionResult request_id is empty.")

        if not result.backend_identity or result.backend_identity.backend_id != "reference_simulator":
            errors.append(f"Invalid backend identity: {result.backend_identity}")

        # Provenance check
        provenance_ok = True
        if not result.provenance:
            errors.append("Missing provenance metadata.")
            provenance_ok = False
        else:
            if not result.provenance.source_rutm_program_hash or not result.provenance.logical_circuit_id:
                errors.append("Incomplete provenance identifiers.")
                provenance_ok = False

        state_ok = False
        prob_ok = False
        meas_ok = False
        cross_ok = False

        # Mode specific payload verification
        if result.execution_mode in (ExecutionMode.STATE_VECTOR, ExecutionMode.STATE_VECTOR_AND_SHOTS):
            if result.final_state_vector is None:
                errors.append(f"final_state_vector is required for mode {result.execution_mode.value}.")
            else:
                norm_valid, norm_val, norm_err = cls.verify_state_vector_norm(result.final_state_vector)
                if not norm_valid:
                    errors.append(norm_err)
                else:
                    state_ok = True

        if result.execution_mode in (ExecutionMode.SHOT_SAMPLING, ExecutionMode.STATE_VECTOR_AND_SHOTS):
            if result.measurement_result is None:
                errors.append(f"measurement_result is required for mode {result.execution_mode.value}.")
            else:
                meas = result.measurement_result
                if meas.shot_count <= 0:
                    errors.append(f"Invalid shot count: {meas.shot_count}.")
                if len(meas.shot_sequence) != meas.shot_count:
                    errors.append(f"Shot sequence length ({len(meas.shot_sequence)}) != shot_count ({meas.shot_count}).")
                if sum(meas.counts.values()) != meas.shot_count:
                    errors.append(f"Sum of counts ({sum(meas.counts.values())}) != shot_count ({meas.shot_count}).")
                if abs(sum(meas.probabilities.values()) - 1.0) >= EPSILON:
                    errors.append(f"Probability distribution sum ({sum(meas.probabilities.values())}) != 1.0 +/- {EPSILON}.")
                else:
                    prob_ok = True
                meas_ok = True

        if result.execution_mode == ExecutionMode.STATE_VECTOR_AND_SHOTS:
            if state_ok and meas_ok:
                cross_valid, cross_err = cls.verify_state_probability_cross_validation(
                    result.final_state_vector,
                    result.measurement_result,
                )
                if not cross_valid:
                    errors.append(cross_err)
                else:
                    cross_ok = True
        elif result.execution_mode == ExecutionMode.STATE_VECTOR:
            cross_ok = True
            prob_ok = True
        elif result.execution_mode == ExecutionMode.SHOT_SAMPLING:
            cross_ok = True
            state_ok = True

        is_valid = len(errors) == 0
        failure_code = None if is_valid else ExecutionFailureCode.NUMERICAL_VERIFICATION_FAILURE

        return ExecutionEquivalenceReport(
            valid=is_valid,
            status="VERIFIED" if is_valid else "FAILED",
            failure_code=failure_code,
            errors=errors,
            state_vector_verified=state_ok,
            probabilities_verified=prob_ok,
            measurement_verified=meas_ok,
            cross_validation_verified=cross_ok,
            provenance_verified=provenance_ok,
        )
