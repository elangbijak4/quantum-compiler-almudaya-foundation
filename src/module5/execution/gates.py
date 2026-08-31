"""
Module 5 Stage 5 — In-Process State-Vector Gate Transformations.

Implements state-vector gate application algorithms operating under big-endian bit indexing.
"""

from typing import List, Tuple, Dict
import math
import cmath
from src.module5.execution.state import QuantumState
from src.module5.native.model import NativeOperation


def apply_x(state: QuantumState, target: int) -> QuantumState:
    """Applies Pauli-X gate to target qubit."""
    N = state.num_qubits()
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = [0.0 + 0.0j] * dim
    shift = N - 1 - target

    for i in range(dim):
        t_bit = (i >> shift) & 1
        new_t_bit = t_bit ^ 1
        j = (i & ~(1 << shift)) | (new_t_bit << shift)
        vec_out[j] = vec_in[i]

    return QuantumState(vec_out, N)


def apply_cnot(state: QuantumState, control: int, target: int) -> QuantumState:
    """Applies CNOT gate with control and target qubits."""
    N = state.num_qubits()
    if control < 0 or control >= N:
        raise ValueError(f"Control qubit index out of bounds [0, {N-1}]: {control}")
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")
    if control == target:
        raise ValueError(f"Control and target qubit collision: control {control} == target {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = [0.0 + 0.0j] * dim
    c_shift = N - 1 - control
    t_shift = N - 1 - target

    for i in range(dim):
        c_bit = (i >> c_shift) & 1
        if c_bit == 1:
            t_bit = (i >> t_shift) & 1
            new_t_bit = t_bit ^ 1
            j = (i & ~(1 << t_shift)) | (new_t_bit << t_shift)
            vec_out[j] = vec_in[i]
        else:
            vec_out[i] = vec_in[i]

    return QuantumState(vec_out, N)


def apply_swap(state: QuantumState, qubit_a: int, qubit_b: int) -> QuantumState:
    """Applies SWAP gate between qubit_a and qubit_b."""
    N = state.num_qubits()
    if qubit_a < 0 or qubit_a >= N:
        raise ValueError(f"Qubit A index out of bounds [0, {N-1}]: {qubit_a}")
    if qubit_b < 0 or qubit_b >= N:
        raise ValueError(f"Qubit B index out of bounds [0, {N-1}]: {qubit_b}")
    if qubit_a == qubit_b:
        raise ValueError(f"SWAP qubit collision: qubit_a {qubit_a} == qubit_b {qubit_b}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = [0.0 + 0.0j] * dim
    a_shift = N - 1 - qubit_a
    b_shift = N - 1 - qubit_b

    for i in range(dim):
        a_bit = (i >> a_shift) & 1
        b_bit = (i >> b_shift) & 1
        new_i = (i & ~(1 << a_shift) & ~(1 << b_shift)) | (b_bit << a_shift) | (a_bit << b_shift)
        vec_out[new_i] = vec_in[i]

    return QuantumState(vec_out, N)


def apply_toffoli(state: QuantumState, control1: int, control2: int, target: int) -> QuantumState:
    """Applies TOFFOLI gate with control1, control2, and target qubits."""
    N = state.num_qubits()
    if control1 < 0 or control1 >= N:
        raise ValueError(f"Control 1 index out of bounds [0, {N-1}]: {control1}")
    if control2 < 0 or control2 >= N:
        raise ValueError(f"Control 2 index out of bounds [0, {N-1}]: {control2}")
    if target < 0 or target >= N:
        raise ValueError(f"Target index out of bounds [0, {N-1}]: {target}")
    if len({control1, control2, target}) != 3:
        raise ValueError(f"TOFFOLI control/target collision: controls=({control1}, {control2}), target={target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = [0.0 + 0.0j] * dim
    c1_shift = N - 1 - control1
    c2_shift = N - 1 - control2
    t_shift = N - 1 - target

    for i in range(dim):
        c1_bit = (i >> c1_shift) & 1
        c2_bit = (i >> c2_shift) & 1
        if c1_bit == 1 and c2_bit == 1:
            t_bit = (i >> t_shift) & 1
            new_t_bit = t_bit ^ 1
            j = (i & ~(1 << t_shift)) | (new_t_bit << t_shift)
            vec_out[j] = vec_in[i]
        else:
            vec_out[i] = vec_in[i]

    return QuantumState(vec_out, N)


def apply_h(state: QuantumState, target: int) -> QuantumState:
    """Applies Hadamard (H) gate to target qubit."""
    N = state.num_qubits()
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = [0.0 + 0.0j] * dim
    shift = N - 1 - target
    inv_sqrt2 = 1.0 / math.sqrt(2)

    for i in range(dim):
        if ((i >> shift) & 1) == 0:
            i0 = i
            i1 = i | (1 << shift)
            a0 = vec_in[i0]
            a1 = vec_in[i1]
            vec_out[i0] = inv_sqrt2 * (a0 + a1)
            vec_out[i1] = inv_sqrt2 * (a0 - a1)

    return QuantumState(vec_out, N)


def apply_z(state: QuantumState, target: int) -> QuantumState:
    """Applies Pauli-Z gate to target qubit."""
    N = state.num_qubits()
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = list(vec_in)
    shift = N - 1 - target

    for i in range(dim):
        if ((i >> shift) & 1) == 1:
            vec_out[i] = -vec_in[i]

    return QuantumState(vec_out, N)


def apply_s(state: QuantumState, target: int) -> QuantumState:
    """Applies Phase-S gate to target qubit."""
    N = state.num_qubits()
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = list(vec_in)
    shift = N - 1 - target

    for i in range(dim):
        if ((i >> shift) & 1) == 1:
            vec_out[i] = 1j * vec_in[i]

    return QuantumState(vec_out, N)


def apply_t(state: QuantumState, target: int) -> QuantumState:
    """Applies Phase-T gate to target qubit."""
    N = state.num_qubits()
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = list(vec_in)
    shift = N - 1 - target
    t_phase = cmath.exp(1j * math.pi / 4)

    for i in range(dim):
        if ((i >> shift) & 1) == 1:
            vec_out[i] = t_phase * vec_in[i]

    return QuantumState(vec_out, N)


def apply_cz(state: QuantumState, control: int, target: int) -> QuantumState:
    """Applies CZ gate with control and target qubits."""
    N = state.num_qubits()
    if control < 0 or control >= N:
        raise ValueError(f"Control qubit index out of bounds [0, {N-1}]: {control}")
    if target < 0 or target >= N:
        raise ValueError(f"Target qubit index out of bounds [0, {N-1}]: {target}")
    if control == target:
        raise ValueError(f"Control and target qubit collision: control {control} == target {target}")

    dim = state.dimension()
    vec_in = state.vector()
    vec_out = list(vec_in)
    c_shift = N - 1 - control
    t_shift = N - 1 - target

    for i in range(dim):
        if ((i >> c_shift) & 1) == 1 and ((i >> t_shift) & 1) == 1:
            vec_out[i] = -vec_in[i]

    return QuantumState(vec_out, N)


def apply_native_operation(state: QuantumState, op: NativeOperation) -> QuantumState:
    """Dispatches a NativeOperation to the corresponding state-vector gate application function."""
    gate_name = op.native_gate.upper()
    operands = op.operands

    if gate_name == "X":
        if len(operands) != 1:
            raise ValueError(f"X gate expects 1 operand, got {len(operands)}")
        return apply_x(state, operands[0])

    elif gate_name == "CNOT":
        if len(operands) != 2:
            raise ValueError(f"CNOT gate expects 2 operands (control, target), got {len(operands)}")
        return apply_cnot(state, operands[0], operands[1])

    elif gate_name == "SWAP":
        if len(operands) != 2:
            raise ValueError(f"SWAP gate expects 2 operands, got {len(operands)}")
        return apply_swap(state, operands[0], operands[1])

    elif gate_name == "TOFFOLI":
        if len(operands) != 3:
            raise ValueError(f"TOFFOLI gate expects 3 operands (c1, c2, target), got {len(operands)}")
        return apply_toffoli(state, operands[0], operands[1], operands[2])

    elif gate_name == "H":
        if len(operands) != 1:
            raise ValueError(f"H gate expects 1 operand, got {len(operands)}")
        return apply_h(state, operands[0])

    elif gate_name == "Z":
        if len(operands) != 1:
            raise ValueError(f"Z gate expects 1 operand, got {len(operands)}")
        return apply_z(state, operands[0])

    elif gate_name == "S":
        if len(operands) != 1:
            raise ValueError(f"S gate expects 1 operand, got {len(operands)}")
        return apply_s(state, operands[0])

    elif gate_name == "T":
        if len(operands) != 1:
            raise ValueError(f"T gate expects 1 operand, got {len(operands)}")
        return apply_t(state, operands[0])

    elif gate_name == "CZ":
        if len(operands) != 2:
            raise ValueError(f"CZ gate expects 2 operands, got {len(operands)}")
        return apply_cz(state, operands[0], operands[1])

    else:
        raise ValueError(f"Unsupported native gate operation for state-vector engine: '{op.native_gate}'")
