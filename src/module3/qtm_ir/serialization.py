"""
QTM-IR Deterministic Canonical Serialization & Deserialization (Module 3 Stage 5).

Provides deterministic JSON & dictionary serialization for QTM-IR models,
guaranteeing round-trip semantic equality deserialize(serialize(model)) == model.
"""

import json
from typing import Dict, Any, List, Optional, Tuple

from src.module1.utm.model import Direction
from src.module2.rutm.model import HistoryRecord
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    QTM_IR_VERSION,
)


def _serialize_history_item(item: Any) -> Any:
    """Helper converting history record/dict/tuple into canonical JSON-serializable dict."""
    if isinstance(item, HistoryRecord) or hasattr(item, "prev_state"):
        dir_val = item.direction.value if hasattr(item.direction, "value") else str(item.direction)
        return {
            "direction": str(dir_val),
            "overwritten_symbol": str(item.overwritten_symbol),
            "prev_state": str(item.prev_state),
        }
    elif isinstance(item, dict):
        return {str(k): str(v) for k, v in sorted(item.items())}
    elif isinstance(item, (list, tuple)):
        return [str(x) for x in item]
    else:
        return str(item)


def serialize_qtm_ir(model: QTMIRModel) -> Dict[str, Any]:
    """
    Serializes a QTMIRModel instance into a canonical deterministic Python dictionary.

    :param model: QTMIRModel instance.
    :return: Deterministically sorted dictionary.
    """
    if not isinstance(model, QTMIRModel):
        raise TypeError(f"serialize_qtm_ir requires a QTMIRModel instance, got {type(model).__name__}.")

    # Deterministically ordered basis states
    sorted_basis_ids = sorted(model.basis_states.keys())
    basis_states_dict = {}
    for b_id in sorted_basis_ids:
        b_state = model.basis_states[b_id]
        sorted_tape = {str(k): str(v) for k, v in sorted(b_state.tape.items(), key=lambda item: item[0])}
        serialized_history = [_serialize_history_item(h) for h in b_state.history]
        basis_states_dict[b_id] = {
            "basis_id": b_state.basis_id,
            "current_state": b_state.current_state,
            "tape": sorted_tape,
            "head_pos": b_state.head_pos,
            "history": serialized_history,
            "step_count": b_state.step_count,
            "halted": b_state.halted,
            "error": b_state.error,
        }

    # Deterministically ordered state vector amplitudes
    v_init = model.initial_state_vector
    sorted_amp_keys = sorted(v_init.amplitudes.keys())
    amps_dict = {}
    for ref_id in sorted_amp_keys:
        c_val = v_init.amplitudes[ref_id]
        amps_dict[ref_id] = {
            "real": float(c_val.real),
            "imag": float(c_val.imag),
        }

    state_vector_dict = {
        "amplitudes": amps_dict,
        "tolerance": float(v_init.tolerance),
        "is_normalized": bool(v_init.is_normalized),
    }

    # Deterministically ordered transition mapping
    t_map = model.transition_mapping
    sorted_fwd = {k: t_map.forward_mapping[k] for k in sorted(t_map.forward_mapping.keys())}
    sorted_rev = {k: t_map.reverse_mapping[k] for k in sorted(t_map.reverse_mapping.keys())}
    transition_mapping_dict = {
        "forward_mapping": sorted_fwd,
        "reverse_mapping": sorted_rev,
        "is_bijective": bool(t_map.is_bijective),
    }

    # Matrix representation if present
    matrix_rep_dict = None
    if model.matrix_representation is not None:
        m_rep = model.matrix_representation
        serialized_matrix = [
            [{"real": float(c.real), "imag": float(c.imag)} for c in row]
            for row in m_rep.matrix
        ]
        matrix_rep_dict = {
            "basis_order": list(m_rep.basis_order),
            "matrix": serialized_matrix,
            "dimension": int(m_rep.dimension),
        }

    # Provenance if present
    provenance_dict = None
    if model.provenance is not None:
        prov = model.provenance
        provenance_dict = {
            "source_rutm_program_hash": prov.source_rutm_program_hash,
            "source_module": prov.source_module,
            "stage": prov.stage,
            "compiler_version": prov.compiler_version,
            "semantic_relation": prov.semantic_relation,
        }

    return {
        "version": model.version,
        "machine_id": model.machine_id,
        "basis_states": basis_states_dict,
        "initial_state_vector": state_vector_dict,
        "transition_mapping": transition_mapping_dict,
        "matrix_representation": matrix_rep_dict,
        "provenance": provenance_dict,
    }


def deserialize_qtm_ir(data: Dict[str, Any]) -> QTMIRModel:
    """
    Deserializes a Python dictionary into a canonical QTMIRModel instance.

    :param data: Dictionary containing QTM-IR data.
    :return: QTMIRModel instance.
    """
    if not isinstance(data, dict):
        raise TypeError(f"deserialize_qtm_ir requires a dict input, got {type(data).__name__}.")

    version = data.get("version", QTM_IR_VERSION)
    machine_id = data.get("machine_id", "qtm_instance")

    # Basis states
    raw_basis = data.get("basis_states", {})
    basis_states = {}
    for b_id, raw_b in raw_basis.items():
        raw_tape = raw_b.get("tape", {})
        tape = {int(k): str(v) for k, v in raw_tape.items()}
        raw_hist = raw_b.get("history", [])
        history_list = []
        for h_item in raw_hist:
            if isinstance(h_item, dict) and "prev_state" in h_item and "overwritten_symbol" in h_item and "direction" in h_item:
                dir_str = h_item["direction"]
                try:
                    dir_obj = Direction(dir_str)
                except ValueError:
                    dir_obj = dir_str
                history_list.append(
                    HistoryRecord(
                        prev_state=str(h_item["prev_state"]),
                        overwritten_symbol=str(h_item["overwritten_symbol"]),
                        direction=dir_obj,
                    )
                )
            else:
                history_list.append(h_item)
        history = tuple(history_list)
        basis_states[b_id] = QTMIRBasisState(
            basis_id=raw_b.get("basis_id", b_id),
            current_state=raw_b.get("current_state", "q_start"),
            tape=tape,
            head_pos=raw_b.get("head_pos", 0),
            history=history,
            step_count=raw_b.get("step_count", 0),
            halted=raw_b.get("halted", False),
            error=raw_b.get("error", None),
        )

    # Initial state vector
    raw_v = data.get("initial_state_vector", {})
    raw_amps = raw_v.get("amplitudes", {})
    amplitudes = {}
    for ref_id, raw_amp in raw_amps.items():
        amplitudes[ref_id] = QTMIRComplexNumber(
            real=float(raw_amp.get("real", 0.0)),
            imag=float(raw_amp.get("imag", 0.0)),
        )
    initial_state_vector = QTMIRStateVector(
        amplitudes=amplitudes,
        tolerance=float(raw_v.get("tolerance", 1e-12)),
        is_normalized=bool(raw_v.get("is_normalized", True)),
    )

    # Transition mapping
    raw_t = data.get("transition_mapping", {})
    transition_mapping = QTMIRTransitionMapping(
        forward_mapping=dict(raw_t.get("forward_mapping", {})),
        reverse_mapping=dict(raw_t.get("reverse_mapping", {})),
        is_bijective=bool(raw_t.get("is_bijective", True)),
    )

    # Matrix representation
    matrix_representation = None
    raw_m = data.get("matrix_representation")
    if raw_m is not None:
        basis_order = list(raw_m.get("basis_order", []))
        raw_mat = raw_m.get("matrix", [])
        matrix = [
            [QTMIRComplexNumber(real=float(c.get("real", 0.0)), imag=float(c.get("imag", 0.0))) for c in row]
            for row in raw_mat
        ]
        matrix_representation = QTMIRMatrixRepresentation(
            basis_order=basis_order,
            matrix=matrix,
            dimension=raw_m.get("dimension", len(basis_order)),
        )

    # Provenance
    provenance = None
    raw_p = data.get("provenance")
    if raw_p is not None:
        provenance = QTMIRProvenance(
            source_rutm_program_hash=raw_p.get("source_rutm_program_hash", ""),
            source_module=raw_p.get("source_module", "Module 2 (RUTM-IR)"),
            stage=raw_p.get("stage", "Stage 5 (QTM-IR Model)"),
            compiler_version=raw_p.get("compiler_version", "0.3.0-alpha"),
            semantic_relation=raw_p.get("semantic_relation", "Canonical QTM Lifting (U_P ∘ ι = ι ∘ R_P)"),
        )

    return QTMIRModel(
        version=version,
        machine_id=machine_id,
        basis_states=basis_states,
        initial_state_vector=initial_state_vector,
        transition_mapping=transition_mapping,
        matrix_representation=matrix_representation,
        provenance=provenance,
    )


def serialize_qtm_ir_to_json(model: QTMIRModel, indent: int = 2) -> str:
    """
    Serializes a QTMIRModel instance to a canonical JSON string.

    :param model: QTMIRModel instance.
    :return: Canonical JSON string.
    """
    data = serialize_qtm_ir(model)
    return json.dumps(data, indent=indent, sort_keys=True)


def deserialize_qtm_ir_from_json(json_str: str) -> QTMIRModel:
    """
    Deserializes a JSON string into a QTMIRModel instance.

    :param json_str: JSON string.
    :return: QTMIRModel instance.
    """
    data = json.loads(json_str)
    return deserialize_qtm_ir(data)
