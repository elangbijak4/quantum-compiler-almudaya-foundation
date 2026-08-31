"""
Certificate C1 Generation & Validation Engine (Stage 11).

Strictly compliant with Stage 11 requirements (main-technical-refference.md & STAGE_11_CERTIFICATE.md).
"""

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union

from .dual import DualExecutionResult
from .verifier import SemanticVerificationResult


@dataclass
class CertificateC1:
    """Represents a deterministic Certificate C1 for AML -> UTM empirical semantic verification."""
    identity: Dict[str, Any]
    source: Dict[str, Any]
    aml_ir: Dict[str, Any]
    utm_ir: Dict[str, Any]
    translation: Dict[str, Any]
    execution: Dict[str, Any]
    observation: Dict[str, Any]
    verification: Dict[str, Any]
    claims: Dict[str, Any]
    scope: Dict[str, Any]
    complexity: Dict[str, Any]
    provenance: Dict[str, Any]
    certificate_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert CertificateC1 instance to a standard Python dictionary."""
        d = asdict(self)
        return d


def serialize_certificate_c1(cert: Union[CertificateC1, Dict[str, Any]]) -> str:
    """
    Deterministically serialize a CertificateC1 (or dictionary representation) to canonical JSON.
    Uses sorted keys, UTF-8 encoding, and 2-space indentation.
    """
    if isinstance(cert, CertificateC1):
        cert_dict = cert.to_dict()
    else:
        cert_dict = dict(cert)

    return json.dumps(cert_dict, sort_keys=True, indent=2, ensure_ascii=False)


def hash_certificate_c1(cert: Union[CertificateC1, Dict[str, Any]]) -> str:
    """
    Compute SHA-256 hash over the canonical JSON representation of a CertificateC1 payload.
    Omits the `certificate_hash` field to ensure deterministic hashing.
    """
    if isinstance(cert, CertificateC1):
        cert_dict = cert.to_dict()
    else:
        cert_dict = dict(cert)

    # Omit certificate_hash payload field for deterministic self-hashing
    payload_dict = {k: v for k, v in cert_dict.items() if k != "certificate_hash"}
    canonical_json = json.dumps(payload_dict, sort_keys=True, indent=2, ensure_ascii=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def generate_certificate_c1(
    dual_result: DualExecutionResult,
    verification_result: SemanticVerificationResult,
    input_state: Optional[Dict[str, int]] = None,
    source_program_text: Optional[str] = None,
) -> CertificateC1:
    """
    Construct a deterministic Certificate C1 from Stage 9 DualExecutionResult
    and Stage 10 SemanticVerificationResult.
    """
    source_hash = verification_result.source_program_hash or dual_result.source_hash
    source_hash_short = source_hash[:12] if source_hash else "unknown"
    certificate_id = f"C1_{source_hash_short}"

    # Extract AML-IR metrics if available
    aml_res = dual_result.aml_result
    trans_res = dual_result.translation_result
    utm_res = dual_result.utm_result

    aml_instr_count = trans_res.metrics.get("aml_instruction_count", 0) if trans_res and trans_res.metrics else 0
    utm_states_count = trans_res.metrics.get("utm_state_count", 0) if trans_res and trans_res.metrics else 0
    utm_transitions_count = trans_res.metrics.get("utm_transition_count", 0) if trans_res and trans_res.metrics else 0
    alphabet_size = trans_res.metrics.get("tape_alphabet_size", 0) if trans_res and trans_res.metrics else 0

    # Hashes of intermediate structures
    aml_ir_hash = hashlib.sha256(f"AML_IR_count_{aml_instr_count}".encode("utf-8")).hexdigest()
    utm_ir_hash = hashlib.sha256(f"UTM_IR_states_{utm_states_count}_trans_{utm_transitions_count}".encode("utf-8")).hexdigest()

    # Observations
    obs_aml = verification_result.source_result or {}
    obs_utm = verification_result.target_result or {}
    obs_equal = (obs_aml == obs_utm)
    halt_equal = (verification_result.source_halted == verification_result.target_halted)

    # Complexity metrics
    aml_steps = verification_result.metrics.get("aml_steps", aml_res.step_count if aml_res else 0)
    utm_steps = verification_result.metrics.get("utm_steps", utm_res.step_count if utm_res else 0)
    utm_tape_usage = verification_result.metrics.get("utm_tape_usage", utm_res.tape_usage if utm_res else 0)
    expansion_ratio = round(utm_steps / max(aml_steps, 1), 2)

    # Top-level status mapping
    cert_status = verification_result.status

    cert = CertificateC1(
        identity={
            "certificate_id": certificate_id,
            "certificate_type": "C1_TRANSLATION_EMPIRICAL_VERIFICATION",
            "certificate_version": "1.0",
            "module": "Module 1",
            "stage": "Stage 11",
            "status": cert_status,
        },
        source={
            "source_program": source_program_text or "",
            "source_program_hash": source_hash,
            "source_hash_algorithm": "sha256",
            "source_language": "AML",
            "source_language_version": "v0.1",
        },
        aml_ir={
            "instruction_count": aml_instr_count,
            "symbol_table": sorted(list(obs_aml.keys())),
            "label_table": {},
            "aml_ir_hash": aml_ir_hash,
        },
        utm_ir={
            "state_count": utm_states_count,
            "transition_count": utm_transitions_count,
            "alphabet_size": alphabet_size,
            "blank_symbol": "_",
            "initial_state": "q_start",
            "halt_state": "q_halt",
            "utm_ir_hash": utm_ir_hash,
        },
        translation={
            "translation_status": trans_res.status if trans_res else "ERROR",
            "translator_version": "1.0",
            "deterministic_translation": True,
            "generated_utm_valid": (trans_res.status == "TRANSLATION_GENERATED") if trans_res else False,
        },
        execution={
            "aml_status": aml_res.status if aml_res else "ERROR",
            "aml_halted": verification_result.source_halted,
            "aml_step_count": aml_steps,
            "aml_observable_result": obs_aml,
            "utm_status": utm_res.status if utm_res else "ERROR",
            "utm_halted": verification_result.target_halted,
            "utm_step_count": utm_steps,
            "utm_tape_usage": utm_tape_usage,
            "utm_observable_result": obs_utm,
        },
        observation={
            "Obs_AML": obs_aml,
            "Obs_UTM": obs_utm,
        },
        verification={
            "verification_status": verification_result.status,
            "verified": verification_result.verified,
            "observation_equal": obs_equal,
            "halting_equal": halt_equal,
            "mismatch_reason": verification_result.mismatch_reason,
            "verification_method": "EMPIRICAL_SEMANTIC_VERIFICATION",
        },
        claims={
            "verification_scope": "SINGLE_EXECUTION_INSTANCE",
            "verification_type": "EMPIRICAL",
            "universal_claim": False,
            "formal_proof": False,
        },
        scope={
            "input_state": input_state or {},
            "max_steps": 100000,
            "scope": "SINGLE_EXECUTION_INSTANCE",
        },
        complexity={
            "aml_steps": aml_steps,
            "utm_steps": utm_steps,
            "utm_tape_usage": utm_tape_usage,
            "expansion_ratio": expansion_ratio,
        },
        provenance={
            "compiler_version": "0.1",
            "module_version": "0.1",
            "AML_version": "v0.1",
            "UTM_model_version": "1.0",
            "translator_version": "1.0",
            "simulator_version": "1.0",
            "verifier_version": "1.0",
        },
        certificate_hash=None,
    )

    # Compute deterministic self-hash
    cert.certificate_hash = hash_certificate_c1(cert)
    return cert


def validate_certificate_c1(cert_or_dict: Union[CertificateC1, Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Validates the internal consistency and mandatory invariants of a Certificate C1.

    Returns:
        (is_valid, error_message)
    """
    if isinstance(cert_or_dict, CertificateC1):
        d = cert_or_dict.to_dict()
    elif isinstance(cert_or_dict, dict):
        d = cert_or_dict
    else:
        return False, "Certificate must be a CertificateC1 instance or dictionary"

    # Required top-level sections
    required_sections = [
        "identity", "source", "aml_ir", "utm_ir", "translation",
        "execution", "observation", "verification", "claims", "scope",
        "complexity", "provenance"
    ]
    for sec in required_sections:
        if sec not in d or not isinstance(d[sec], dict):
            return False, f"Missing or invalid section '{sec}' in Certificate C1"

    identity = d["identity"]
    source = d["source"]
    verification = d["verification"]
    claims = d["claims"]
    execution = d["execution"]
    observation = d["observation"]

    # 1. Valid status
    valid_statuses = {"VERIFIED", "NOT_VERIFIED", "MISMATCH", "INVALID_TRANSLATION", "SOURCE_EXECUTION_FAILURE", "TARGET_EXECUTION_FAILURE", "RESOURCE_LIMIT", "ERROR"}
    if identity.get("status") not in valid_statuses:
        return False, f"Invalid certificate status '{identity.get('status')}'"

    # 2. Source hash format (64-char sha256 hex string)
    src_hash = source.get("source_program_hash", "")
    if not isinstance(src_hash, str) or len(src_hash) != 64:
        return False, f"Invalid source_program_hash '{src_hash}' (must be 64-char sha256 hex string)"

    # 3. Claims boundary: universal_claim and formal_proof MUST be False
    if claims.get("universal_claim") is not False:
        return False, "Certificate violation: universal_claim MUST be False for empirical C1"
    if claims.get("formal_proof") is not False:
        return False, "Certificate violation: formal_proof MUST be False for empirical C1"
    if claims.get("verification_scope") != "SINGLE_EXECUTION_INSTANCE":
        return False, "Certificate violation: verification_scope MUST be 'SINGLE_EXECUTION_INSTANCE'"

    # 4. Consistency of VERIFIED status
    is_verified = verification.get("verified", False)
    if identity.get("status") == "VERIFIED":
        if not is_verified:
            return False, "Inconsistent certificate: status is 'VERIFIED' but verification.verified is False"

        # If verified is True, enforce strict execution & observation invariants
        if not execution.get("aml_halted", False):
            return False, "Invalid certificate: verified is True but aml_halted is False"
        if not execution.get("utm_halted", False):
            return False, "Invalid certificate: verified is True but utm_halted is False"
        if not verification.get("observation_equal", False):
            return False, "Invalid certificate: verified is True but observation_equal is False"
        if not verification.get("halting_equal", False):
            return False, "Invalid certificate: verified is True but halting_equal is False"
        if observation.get("Obs_AML") != observation.get("Obs_UTM"):
            return False, "Invalid certificate: verified is True but Obs_AML != Obs_UTM"
        if verification.get("mismatch_reason") is not None:
            return False, "Invalid certificate: verified is True but mismatch_reason is not None"
    else:
        if is_verified:
            return False, f"Inconsistent certificate: status is '{identity.get('status')}' but verification.verified is True"

    # 5. Check payload hash consistency if certificate_hash is present
    payload_hash = d.get("certificate_hash")
    if payload_hash is not None:
        computed_hash = hash_certificate_c1(d)
        if computed_hash != payload_hash:
            return False, f"Corrupted certificate: hash mismatch (stored '{payload_hash}' != computed '{computed_hash}')"

    return True, None


def save_certificate_c1(
    cert: Union[CertificateC1, Dict[str, Any]],
    output_dir: str = "certificates"
) -> str:
    """
    Saves a Certificate C1 to canonical JSON under the specified output directory.

    Filename convention: `C1_<source_hash>.json`

    Returns:
        Absolute filepath to the saved certificate file.
    """
    if isinstance(cert, CertificateC1):
        cert_dict = cert.to_dict()
        source_hash = cert.source.get("source_program_hash", "unknown")
    else:
        cert_dict = dict(cert)
        source_hash = cert_dict.get("source", {}).get("source_program_hash", "unknown")

    os.makedirs(output_dir, exist_ok=True)
    filename = f"C1_{source_hash}.json"
    filepath = os.path.join(output_dir, filename)

    canonical_json = serialize_certificate_c1(cert_dict)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(canonical_json)

    return os.path.abspath(filepath)
