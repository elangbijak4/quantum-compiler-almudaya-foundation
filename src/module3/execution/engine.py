"""
QTM Execution Engine & State Vector Evolution (Module 3 Stage 7).

Evolves Quantum Turing Machine state vectors according to validated unitary
transition operator U_P and adjoint operator U_P^dagger over Hilbert space H_Q = l^2(C_R).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, Union
import math

from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRComplexNumber,
)
from src.module3.qtm_ir.validator import validate_qtm_ir, ValidationResult


class QTMExecutionError(ValueError):
    """Raised when QTM execution fails or encounters invalid QTM-IR / state vector."""
    pass


@dataclass
class QTMExecutionTrace:
    """
    Execution trace output contract storing quantum state evolution history |ψ(0)>, ..., |ψ(T)>.
    """
    states: List[QTMIRStateVector] = field(default_factory=list)
    step_count: int = 0
    initial_state: QTMIRStateVector = field(default_factory=QTMIRStateVector)
    final_state: QTMIRStateVector = field(default_factory=QTMIRStateVector)
    norm_trace: List[float] = field(default_factory=list)
    halted: bool = False


def _validate_model_for_execution(model: QTMIRModel) -> None:
    """Helper validating model prior to execution gate."""
    val_res = validate_qtm_ir(model)
    if not val_res.valid:
        errors = [d.message for d in val_res.diagnostics]
        raise QTMExecutionError(f"Model validation failed before execution: {errors}")


def apply_unitary(model: QTMIRModel, state: QTMIRStateVector) -> QTMIRStateVector:
    """
    Applies validated unitary transition operator U_P to quantum state vector |ψ>:
    U_P |ψ> = Σ_i α_i |R_P(B_i)>.

    Accumulates amplitudes for duplicate targets while preserving linearity and norm.
    """
    _validate_model_for_execution(model)

    accumulated: Dict[str, complex] = {}
    f_map = model.transition_mapping.forward_mapping

    for b_id, q_amp in state.amplitudes.items():
        # Check unknown basis ID
        if b_id not in model.basis_states:
            raise QTMExecutionError(f"State vector contains unknown basis ID '{b_id}' not in model basis states.")

        # Check missing transition
        if b_id not in f_map:
            raise QTMExecutionError(f"Model missing forward transition for basis ID '{b_id}'.")

        tgt_id = f_map[b_id]
        if tgt_id not in model.basis_states:
            raise QTMExecutionError(f"Forward mapping target basis ID '{tgt_id}' not in model basis states.")

        c_amp = q_amp.to_complex()
        accumulated[tgt_id] = accumulated.get(tgt_id, 0.0 + 0.0j) + c_amp

    # Filter out numerically negligible amplitudes without forcing automatic normalization
    new_amplitudes: Dict[str, QTMIRComplexNumber] = {}
    for b_id, c_val in accumulated.items():
        if abs(c_val) > state.tolerance:
            new_amplitudes[b_id] = QTMIRComplexNumber.from_complex(c_val)

    return QTMIRStateVector(
        amplitudes=new_amplitudes,
        tolerance=state.tolerance,
        is_normalized=state.is_normalized,
    )


def apply_adjoint(model: QTMIRModel, state: QTMIRStateVector) -> QTMIRStateVector:
    """
    Applies validated adjoint operator U_P^dagger to quantum state vector |ψ>:
    U_P^dagger |ψ'> = Σ_j β_j |R_P^-1(B_j)>.

    Uses validated reverse mapping directly.
    """
    _validate_model_for_execution(model)

    accumulated: Dict[str, complex] = {}
    r_map = model.transition_mapping.reverse_mapping

    for b_id, q_amp in state.amplitudes.items():
        # Check unknown basis ID
        if b_id not in model.basis_states:
            raise QTMExecutionError(f"State vector contains unknown basis ID '{b_id}' not in model basis states.")

        # Check missing transition
        if b_id not in r_map:
            raise QTMExecutionError(f"Model missing reverse transition for basis ID '{b_id}'.")

        prev_id = r_map[b_id]
        if prev_id not in model.basis_states:
            raise QTMExecutionError(f"Reverse mapping predecessor basis ID '{prev_id}' not in model basis states.")

        c_amp = q_amp.to_complex()
        accumulated[prev_id] = accumulated.get(prev_id, 0.0 + 0.0j) + c_amp

    # Filter out numerically negligible amplitudes
    new_amplitudes: Dict[str, QTMIRComplexNumber] = {}
    for b_id, c_val in accumulated.items():
        if abs(c_val) > state.tolerance:
            new_amplitudes[b_id] = QTMIRComplexNumber.from_complex(c_val)

    return QTMIRStateVector(
        amplitudes=new_amplitudes,
        tolerance=state.tolerance,
        is_normalized=state.is_normalized,
    )


def apply_matrix(model: QTMIRModel, state: QTMIRStateVector) -> QTMIRStateVector:
    """
    Matrix cross-validation path: applies dense matrix multiplication [U_P] |ψ>.
    Requires model.matrix_representation.
    """
    _validate_model_for_execution(model)

    if model.matrix_representation is None:
        raise QTMExecutionError("Model matrix_representation is missing for matrix execution.")

    m_rep = model.matrix_representation
    basis_order = m_rep.basis_order
    N = m_rep.dimension
    basis_index_map = {b_id: idx for idx, b_id in enumerate(basis_order)}

    # Check unknown basis states in state
    for b_id in state.amplitudes.keys():
        if b_id not in basis_index_map:
            raise QTMExecutionError(f"State vector contains basis ID '{b_id}' not in matrix basis order.")

    # Build input vector column
    v_in = [0.0 + 0.0j for _ in range(N)]
    for b_id, q_amp in state.amplitudes.items():
        v_in[basis_index_map[b_id]] = q_amp.to_complex()

    # Matrix-vector multiplication v' = [U_P] v
    v_out = [0.0 + 0.0j for _ in range(N)]
    for i in range(N):
        row_sum = 0.0 + 0.0j
        for j in range(N):
            m_val = m_rep.matrix[i][j].to_complex()
            if abs(m_val) > 0.0:
                row_sum += m_val * v_in[j]
        v_out[i] = row_sum

    # Reconstruct QTMIRStateVector
    new_amplitudes: Dict[str, QTMIRComplexNumber] = {}
    for idx, c_val in enumerate(v_out):
        if abs(c_val) > state.tolerance:
            b_id = basis_order[idx]
            new_amplitudes[b_id] = QTMIRComplexNumber.from_complex(c_val)

    return QTMIRStateVector(
        amplitudes=new_amplitudes,
        tolerance=state.tolerance,
        is_normalized=state.is_normalized,
    )


def execute(
    model: QTMIRModel,
    initial_state: Optional[QTMIRStateVector] = None,
    steps: int = 1,
) -> QTMExecutionTrace:
    """
    Executes N-step quantum state evolution: |ψ(t+1)> = U_P |ψ(t)>.

    :param model: Validated QTMIRModel.
    :param initial_state: Optional initial state vector (defaults to model.initial_state_vector).
    :param steps: Number of execution steps (>= 0).
    :return: QTMExecutionTrace instance.
    """
    _validate_model_for_execution(model)

    if steps < 0:
        raise QTMExecutionError(f"Step count must be non-negative, got {steps}.")

    curr_state = initial_state if initial_state is not None else model.initial_state_vector
    
    # Check unknown basis states in initial state
    for b_id in curr_state.amplitudes.keys():
        if b_id not in model.basis_states:
            raise QTMExecutionError(f"Initial state vector contains unknown basis ID '{b_id}'.")

    trace_states: List[QTMIRStateVector] = [curr_state]
    norm_trace: List[float] = [curr_state.compute_norm()]

    for _ in range(steps):
        next_state = apply_unitary(model, curr_state)
        trace_states.append(next_state)
        norm_trace.append(next_state.compute_norm())
        curr_state = next_state

    # Check if final state is halted (all non-zero basis states in final state are halted)
    is_halted = False
    if len(curr_state.amplitudes) > 0:
        is_halted = all(
            b_id in model.basis_states and model.basis_states[b_id].halted
            for b_id in curr_state.amplitudes.keys()
        )

    return QTMExecutionTrace(
        states=trace_states,
        step_count=steps,
        initial_state=trace_states[0],
        final_state=curr_state,
        norm_trace=norm_trace,
        halted=is_halted,
    )


def execute_matrix(
    model: QTMIRModel,
    initial_state: Optional[QTMIRStateVector] = None,
    steps: int = 1,
) -> QTMExecutionTrace:
    """
    Executes N-step matrix-based quantum state evolution for cross-validation.
    """
    _validate_model_for_execution(model)

    if steps < 0:
        raise QTMExecutionError(f"Step count must be non-negative, got {steps}.")

    curr_state = initial_state if initial_state is not None else model.initial_state_vector

    trace_states: List[QTMIRStateVector] = [curr_state]
    norm_trace: List[float] = [curr_state.compute_norm()]

    for _ in range(steps):
        next_state = apply_matrix(model, curr_state)
        trace_states.append(next_state)
        norm_trace.append(next_state.compute_norm())
        curr_state = next_state

    is_halted = False
    if len(curr_state.amplitudes) > 0:
        is_halted = all(
            b_id in model.basis_states and model.basis_states[b_id].halted
            for b_id in curr_state.amplitudes.keys()
        )

    return QTMExecutionTrace(
        states=trace_states,
        step_count=steps,
        initial_state=trace_states[0],
        final_state=curr_state,
        norm_trace=norm_trace,
        halted=is_halted,
    )


def normalize_state(state: QTMIRStateVector) -> QTMIRStateVector:
    """
    Explicit utility normalizing state vector by dividing by norm ||ψ||.
    NOT called automatically by apply_unitary.
    """
    norm = state.compute_norm()
    if norm < state.tolerance:
        raise QTMExecutionError(f"Cannot normalize zero state vector (norm {norm} < tolerance {state.tolerance}).")

    normalized_amps: Dict[str, QTMIRComplexNumber] = {}
    for b_id, q_amp in state.amplitudes.items():
        c_val = q_amp.to_complex() / norm
        normalized_amps[b_id] = QTMIRComplexNumber.from_complex(c_val)

    return QTMIRStateVector(
        amplitudes=normalized_amps,
        tolerance=state.tolerance,
        is_normalized=True,
    )


def inner_product(v1: QTMIRStateVector, v2: QTMIRStateVector) -> QTMIRComplexNumber:
    """
    Computes Hilbert space inner product <v1|v2> = Σ_b (α_b)* β_b.
    """
    total = 0.0 + 0.0j
    for b_id, amp1 in v1.amplitudes.items():
        if b_id in v2.amplitudes:
            c1 = amp1.to_complex()
            c2 = v2.amplitudes[b_id].to_complex()
            total += c1.conjugate() * c2

    return QTMIRComplexNumber.from_complex(total)


class QTMExecutionEngine:
    """
    QTM Execution Engine class providing object-oriented execution API.
    """

    def __init__(self, model: QTMIRModel):
        _validate_model_for_execution(model)
        self.model = model

    def apply_unitary(self, state: QTMIRStateVector) -> QTMIRStateVector:
        """Applies U_P to state."""
        return apply_unitary(self.model, state)

    def apply_adjoint(self, state: QTMIRStateVector) -> QTMIRStateVector:
        """Applies U_P^dagger to state."""
        return apply_adjoint(self.model, state)

    def apply_matrix(self, state: QTMIRStateVector) -> QTMIRStateVector:
        """Applies [U_P] matrix to state."""
        return apply_matrix(self.model, state)

    def execute(self, initial_state: Optional[QTMIRStateVector] = None, steps: int = 1) -> QTMExecutionTrace:
        """Executes N-step evolution."""
        return execute(self.model, initial_state=initial_state, steps=steps)

    def execute_matrix(self, initial_state: Optional[QTMIRStateVector] = None, steps: int = 1) -> QTMExecutionTrace:
        """Executes N-step matrix-based evolution."""
        return execute_matrix(self.model, initial_state=initial_state, steps=steps)

    def inner_product(self, v1: QTMIRStateVector, v2: QTMIRStateVector) -> QTMIRComplexNumber:
        """Computes inner product <v1|v2>."""
        return inner_product(v1, v2)
