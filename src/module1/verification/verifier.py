"""
Semantic Equivalence Verifier Stage 10: Sem_AML(P) = Sem_UTM(T(P)) Empirical Verifier.

Strictly compliant with Stage 10 requirements (main-technical-refference.md Section 9, 25).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..aml.interpreter import AMLInterpreterResult
from ..translation.encoder import decode_aml_state
from ..utm.simulator import UTMExecutionResult
from .dual import DualExecutionResult


@dataclass
class SemanticVerificationResult:
    """Represents the complete result of empirical semantic equivalence verification."""
    status: str  # "VERIFIED", "MISMATCH", "SOURCE_EXECUTION_FAILURE", "TARGET_EXECUTION_FAILURE", "RESOURCE_LIMIT", "INVALID_TRANSLATION", "ERROR"
    verified: bool
    source_result: Optional[Dict[str, int]]
    target_result: Optional[Dict[str, int]]
    source_halted: bool
    target_halted: bool
    mismatch_reason: Optional[str]
    source_program_hash: str
    metrics: Dict[str, Any] = field(default_factory=dict)


def extract_obs_aml(aml_res: AMLInterpreterResult) -> Dict[str, int]:
    """Extract observable output memory dictionary from AML reference interpreter result."""
    return dict(aml_res.observable_output)


def extract_obs_utm(utm_res: UTMExecutionResult) -> Dict[str, int]:
    """Decode UTM final configuration tape and extract observable output memory dictionary."""
    decoded_state = decode_aml_state(utm_res.final_configuration)
    return dict(decoded_state.memory)


def verify_semantic_equivalence(
    dual_result: DualExecutionResult
) -> SemanticVerificationResult:
    """
    Verify empirical semantic equivalence Sem_AML(P) = Sem_UTM(T(P)) for a DualExecutionResult.

    Args:
        dual_result: DualExecutionResult from Stage 9 Dual Execution

    Returns:
        SemanticVerificationResult
    """
    # 1. Handle pipeline errors from Stage 9
    if dual_result.status == "PARSER_ERROR":
        return SemanticVerificationResult(
            status="SOURCE_EXECUTION_FAILURE",
            verified=False,
            source_result=None,
            target_result=None,
            source_halted=False,
            target_halted=False,
            mismatch_reason=f"Parser failure: {dual_result.error}",
            source_program_hash=dual_result.source_hash,
        )

    if dual_result.status == "TRANSLATION_ERROR":
        return SemanticVerificationResult(
            status="INVALID_TRANSLATION",
            verified=False,
            source_result=None,
            target_result=None,
            source_halted=False,
            target_halted=False,
            mismatch_reason=f"Translation failure: {dual_result.error}",
            source_program_hash=dual_result.source_hash,
        )

    if dual_result.status == "SIMULATOR_ERROR":
        return SemanticVerificationResult(
            status="TARGET_EXECUTION_FAILURE",
            verified=False,
            source_result=None,
            target_result=None,
            source_halted=False,
            target_halted=False,
            mismatch_reason=f"Target simulator failure: {dual_result.error}",
            source_program_hash=dual_result.source_hash,
        )

    aml_res = dual_result.aml_result
    utm_res = dual_result.utm_result

    # 2. Resource limit checks
    if aml_res and aml_res.status == "RESOURCE_LIMIT":
        return SemanticVerificationResult(
            status="RESOURCE_LIMIT",
            verified=False,
            source_result=extract_obs_aml(aml_res) if aml_res else None,
            target_result=extract_obs_utm(utm_res) if utm_res else None,
            source_halted=False,
            target_halted=utm_res.halted if utm_res else False,
            mismatch_reason="AML reference execution exceeded max_steps limit",
            source_program_hash=dual_result.source_hash,
        )

    if utm_res and utm_res.status == "RESOURCE_LIMIT":
        return SemanticVerificationResult(
            status="RESOURCE_LIMIT",
            verified=False,
            source_result=extract_obs_aml(aml_res) if aml_res else None,
            target_result=extract_obs_utm(utm_res) if utm_res else None,
            source_halted=aml_res.final_state.flags.halted if aml_res else False,
            target_halted=False,
            mismatch_reason="UTM target simulation exceeded max_steps limit",
            source_program_hash=dual_result.source_hash,
        )

    if not aml_res or not utm_res:
        return SemanticVerificationResult(
            status="ERROR",
            verified=False,
            source_result=None,
            target_result=None,
            source_halted=False,
            target_halted=False,
            mismatch_reason="Incomplete dual execution results",
            source_program_hash=dual_result.source_hash,
        )

    # Extract observations
    obs_aml = extract_obs_aml(aml_res)
    obs_utm = extract_obs_utm(utm_res)

    source_halted = aml_res.final_state.flags.halted
    target_halted = utm_res.halted

    metrics = {
        "aml_steps": aml_res.step_count,
        "utm_steps": utm_res.step_count,
        "utm_tape_usage": utm_res.tape_usage,
        "expansion_ratio": round(utm_res.step_count / max(aml_res.step_count, 1), 2),
    }

    # 3. Halting comparison
    if source_halted != target_halted:
        return SemanticVerificationResult(
            status="MISMATCH",
            verified=False,
            source_result=obs_aml,
            target_result=obs_utm,
            source_halted=source_halted,
            target_halted=target_halted,
            mismatch_reason=f"Halting mismatch: AML halted={source_halted}, UTM halted={target_halted}",
            source_program_hash=dual_result.source_hash,
            metrics=metrics,
        )

    # 4. Output observation comparison
    if obs_aml != obs_utm:
        return SemanticVerificationResult(
            status="MISMATCH",
            verified=False,
            source_result=obs_aml,
            target_result=obs_utm,
            source_halted=source_halted,
            target_halted=target_halted,
            mismatch_reason=f"Observable output mismatch: AML={obs_aml}, UTM={obs_utm}",
            source_program_hash=dual_result.source_hash,
            metrics=metrics,
        )

    # 5. Semantic equivalence VERIFIED
    return SemanticVerificationResult(
        status="VERIFIED",
        verified=True,
        source_result=obs_aml,
        target_result=obs_utm,
        source_halted=source_halted,
        target_halted=target_halted,
        mismatch_reason=None,
        source_program_hash=dual_result.source_hash,
        metrics=metrics,
    )
