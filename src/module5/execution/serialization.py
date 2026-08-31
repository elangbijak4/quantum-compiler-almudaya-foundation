"""
Module 5 Stage 5 Micro-Closure — Deterministic Request & Result Serializer.

Implements byte-for-byte canonical JSON serialization and round-trip deserialization for ExecutionRequest and ExecutionResult.
"""

from typing import Dict, Any, List
import json
from src.module5.backend.model import BackendIdentity, BackendType
from src.module5.physical_ir.model import ExecutionProvenance
from src.module5.native.serialization import serialize_native_circuit_ir, deserialize_native_circuit_ir
from src.module5.execution.model import (
    ExecutionRequest,
    ExecutionResult,
    MeasurementResult,
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    EXECUTION_SCHEMA_VERSION,
)
from src.module5.execution.validator import validate_execution_request, validate_execution_result


def serialize_execution_request(request: ExecutionRequest) -> str:
    """Serializes ExecutionRequest into canonical JSON string."""
    init_state_json = None
    if request.initial_state is not None:
        init_state_json = [{"real": c.real, "imag": c.imag} for c in request.initial_state]

    native_json_str = serialize_native_circuit_ir(request.native_circuit)
    native_dict = json.loads(native_json_str)

    data: Dict[str, Any] = {
        "request_id": request.request_id,
        "native_circuit": native_dict,
        "execution_mode": request.execution_mode.value,
        "initial_state": init_state_json,
        "shots": request.shots,
        "seed": request.seed,
        "target_backend_id": request.target_backend_id,
        "schema_version": request.schema_version,
    }

    return json.dumps(data, indent=2)


def deserialize_execution_request(json_str: str) -> ExecutionRequest:
    """Deserializes canonical JSON string into validated ExecutionRequest."""
    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Deserialization failed: Invalid JSON. Error: {e}")

    if not isinstance(data, dict):
        raise ValueError("Deserialization failed: JSON root must be an object.")

    if data.get("schema_version") != EXECUTION_SCHEMA_VERSION:
        raise ValueError(f"Schema version mismatch: expected '{EXECUTION_SCHEMA_VERSION}', got '{data.get('schema_version')}'.")

    native_circuit_str = json.dumps(data["native_circuit"], indent=2)
    native_circuit = deserialize_native_circuit_ir(native_circuit_str)

    init_state = None
    if data.get("initial_state") is not None:
        init_state = [complex(item["real"], item["imag"]) for item in data["initial_state"]]

    request = ExecutionRequest(
        request_id=data["request_id"],
        native_circuit=native_circuit,
        execution_mode=ExecutionMode(data["execution_mode"]),
        initial_state=init_state,
        shots=data.get("shots", 1000),
        seed=data.get("seed"),
        target_backend_id=data.get("target_backend_id", "reference_simulator"),
        schema_version=data["schema_version"],
    )

    val_res = validate_execution_request(request)
    if not val_res.valid:
        raise ValueError(f"Deserialized ExecutionRequest failed validation: {val_res.errors}")

    return request


def serialize_execution_result(result: ExecutionResult) -> str:
    """Serializes ExecutionResult into canonical JSON string."""
    sv_json = None
    if result.final_state_vector is not None:
        sorted_keys = sorted(result.final_state_vector.keys())
        sv_json = {k: {"real": result.final_state_vector[k].real, "imag": result.final_state_vector[k].imag} for k in sorted_keys}

    meas_json = None
    if result.measurement_result is not None:
        sorted_probs = {k: result.measurement_result.probabilities[k] for k in sorted(result.measurement_result.probabilities.keys())}
        sorted_counts = {k: result.measurement_result.counts[k] for k in sorted(result.measurement_result.counts.keys())}
        meas_json = {
            "probabilities": sorted_probs,
            "counts": sorted_counts,
            "shot_sequence": result.measurement_result.shot_sequence,
            "shot_count": result.measurement_result.shot_count,
            "seed": result.measurement_result.seed,
        }

    b_id = result.backend_identity
    backend_json = {
        "backend_id": b_id.backend_id,
        "backend_name": b_id.backend_name,
        "backend_version": b_id.backend_version,
        "backend_type": b_id.backend_type.value,
    }

    prov_json = None
    if result.provenance is not None:
        p = result.provenance
        prov_json = {
            "source_rutm_program_hash": p.source_rutm_program_hash,
            "source_qtm_machine_id": p.source_qtm_machine_id,
            "logical_circuit_id": p.logical_circuit_id,
            "physical_circuit_id": p.physical_circuit_id,
            "backend_id": p.backend_id,
            "compiler_version": p.compiler_version,
        }

    data: Dict[str, Any] = {
        "request_id": result.request_id,
        "status": result.status.value,
        "execution_mode": result.execution_mode.value,
        "backend_identity": backend_json,
        "final_state_vector": sv_json,
        "measurement_result": meas_json,
        "provenance": prov_json,
        "verification_status": result.verification_status,
        "execution_time_ms": result.execution_time_ms,
        "failure_code": result.failure_code.value if result.failure_code else None,
        "failure_message": result.failure_message,
        "diagnostics": result.diagnostics,
        "schema_version": result.schema_version,
    }

    return json.dumps(data, indent=2)


def deserialize_execution_result(json_str: str) -> ExecutionResult:
    """Deserializes canonical JSON string into validated ExecutionResult."""
    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Deserialization failed: Invalid JSON. Error: {e}")

    if not isinstance(data, dict):
        raise ValueError("Deserialization failed: JSON root must be an object.")

    if data.get("schema_version") != EXECUTION_SCHEMA_VERSION:
        raise ValueError(f"Schema version mismatch: expected '{EXECUTION_SCHEMA_VERSION}', got '{data.get('schema_version')}'.")

    b_data = data["backend_identity"]
    backend_id = BackendIdentity(
        backend_id=b_data["backend_id"],
        backend_name=b_data["backend_name"],
        backend_version=b_data["backend_version"],
        backend_type=BackendType(b_data["backend_type"]),
    )

    sv = None
    if data.get("final_state_vector") is not None:
        sv = {k: complex(v["real"], v["imag"]) for k, v in data["final_state_vector"].items()}

    meas = None
    if data.get("measurement_result") is not None:
        m = data["measurement_result"]
        meas = MeasurementResult(
            probabilities=m["probabilities"],
            counts=m["counts"],
            shot_sequence=m["shot_sequence"],
            shot_count=m["shot_count"],
            seed=m.get("seed"),
        )

    prov = None
    if data.get("provenance") is not None:
        p = data["provenance"]
        prov = ExecutionProvenance(
            source_rutm_program_hash=p["source_rutm_program_hash"],
            source_qtm_machine_id=p["source_qtm_machine_id"],
            logical_circuit_id=p["logical_circuit_id"],
            physical_circuit_id=p.get("physical_circuit_id"),
            backend_id=p.get("backend_id", backend_id.backend_id),
            compiler_version=p.get("compiler_version", "0.5.0-alpha"),
        )

    fc = ExecutionFailureCode(data["failure_code"]) if data.get("failure_code") else None

    result = ExecutionResult(
        request_id=data["request_id"],
        status=ExecutionStatus(data["status"]),
        execution_mode=ExecutionMode(data["execution_mode"]),
        backend_identity=backend_id,
        final_state_vector=sv,
        measurement_result=meas,
        provenance=prov,
        verification_status=data.get("verification_status", False),
        execution_time_ms=data.get("execution_time_ms", 0.0),
        failure_code=fc,
        failure_message=data.get("failure_message"),
        diagnostics=data.get("diagnostics", []),
        schema_version=data["schema_version"],
    )

    val_res = validate_execution_result(result)
    if not val_res.valid:
        raise ValueError(f"Deserialized ExecutionResult failed validation: {val_res.errors}")

    return result
