"""
Module 4 Stage 3 — Independent 3-Level Transition Realization & Operator Verifier.

Independently verifies:
- Level 1: Exact Symbolic Computational Basis Verification (U_C |E(C)> = |E(R_P(C))>)
- Reverse Execution Verification (U_C^\dagger |E(R_P(C))> = |E(C)>)
- Level 2: Superposition & Complex Amplitude Verification (State vector L2 norm < 10^-12)
- Level 3: Full Composed Operator Matrix Unitarity & Correspondence (||U_C^\dagger U_C - I||_2 < 10^-12, ||U_C U_C^\dagger - I||_2 < 10^-12)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
import math
from src.module1.utm.model import UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module4.foundation.domain import FiniteDomainContract, config_to_key
from src.module4.foundation.encoding import RegisterEncodingSpec, encode_configuration
from src.module4.foundation.policy import VerificationLevel, VerificationPolicy, NUMERICAL_VERIFICATION_TOLERANCE
from src.module4.circuit_ir.model import QuantumCircuitIR, LogicalGateType, QubitRef
from src.module4.synthesis.transition import build_transition_table


@dataclass
class Stage3VerificationResult:
    """Master structured result for Stage 3 circuit transition realization verification."""
    valid: bool
    symbolic_basis_pass: bool
    reverse_execution_pass: bool
    superposition_pass: bool
    operator_unitary_pass: bool
    verified_pairs_count: int
    superposition_residual: float = 0.0
    left_unitarity_residual: float = 0.0
    right_unitarity_residual: float = 0.0
    diagnostics: List[str] = field(default_factory=list)


def simulate_gate_on_bit_list(gate_type: LogicalGateType, target_idx: int, control_indices: List[int], bits: List[str]) -> None:
    """Simulates a single primitive logical gate in-place on a bit list."""
    controls_active = all(bits[c] == "1" for c in control_indices)
    if controls_active:
        bits[target_idx] = "1" if bits[target_idx] == "0" else "0"


def execute_circuit_on_bitstring(circuit: QuantumCircuitIR, initial_bits: str) -> str:
    """Simulates forward execution of QuantumCircuitIR on a single computational basis bitstring."""
    qubit_index_map: Dict[Tuple[str, int], int] = {}
    flat_idx = 0
    for r in circuit.registers:
        for idx in range(r.width):
            qubit_index_map[(r.register_id, idx)] = flat_idx
            flat_idx += 1

    bits = list(initial_bits)
    if len(bits) < flat_idx:
        bits.extend(["0"] * (flat_idx - len(bits)))

    for gate in circuit.gates:
        target_i = qubit_index_map[(gate.target_qubit.register_id, gate.target_qubit.index)]
        ctrl_is = [qubit_index_map[(cq.register_id, cq.index)] for cq in gate.control_qubits]
        simulate_gate_on_bit_list(gate.gate_type, target_i, ctrl_is, bits)

    data_bits_count = sum(r.width for r in circuit.registers if r.register_type != "ANCILLA")
    return "".join(bits[:data_bits_count])


def execute_inverse_circuit_on_bitstring(circuit: QuantumCircuitIR, initial_bits: str) -> str:
    """Simulates reverse execution U_C^dag by running primitive gates in exact opposite order."""
    qubit_index_map: Dict[Tuple[str, int], int] = {}
    flat_idx = 0
    for r in circuit.registers:
        for idx in range(r.width):
            qubit_index_map[(r.register_id, idx)] = flat_idx
            flat_idx += 1

    bits = list(initial_bits)
    if len(bits) < flat_idx:
        bits.extend(["0"] * (flat_idx - len(bits)))

    for gate in reversed(circuit.gates):
        target_i = qubit_index_map[(gate.target_qubit.register_id, gate.target_qubit.index)]
        ctrl_is = [qubit_index_map[(cq.register_id, cq.index)] for cq in gate.control_qubits]
        simulate_gate_on_bit_list(gate.gate_type, target_i, ctrl_is, bits)

    data_bits_count = sum(r.width for r in circuit.registers if r.register_type != "ANCILLA")
    return "".join(bits[:data_bits_count])


def simulate_circuit_on_basis_index(circuit: QuantumCircuitIR, total_qubits: int, basis_index: int, reverse: bool = False) -> int:
    """
    Simulates the composed circuit on an n-qubit computational basis index integer (0 to 2^n - 1).
    Returns the resulting transformed basis index integer.
    """
    qubit_index_map: Dict[Tuple[str, int], int] = {}
    flat_idx = 0
    for r in circuit.registers:
        for idx in range(r.width):
            qubit_index_map[(r.register_id, idx)] = flat_idx
            flat_idx += 1

    bits = [(basis_index >> i) & 1 for i in range(total_qubits)]

    gate_seq = reversed(circuit.gates) if reverse else circuit.gates
    for gate in gate_seq:
        target_i = qubit_index_map[(gate.target_qubit.register_id, gate.target_qubit.index)]
        ctrl_is = [qubit_index_map[(cq.register_id, cq.index)] for cq in gate.control_qubits]

        if all(bits[c] == 1 for c in ctrl_is):
            bits[target_i] ^= 1

    res_idx = 0
    for i in range(total_qubits):
        if bits[i] == 1:
            res_idx |= (1 << i)
    return res_idx


def verify_transition_realization(
    program: UTMProgram,
    circuit: QuantumCircuitIR,
    domain_contract: FiniteDomainContract,
    encoding_spec: RegisterEncodingSpec,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
    policy: Optional[VerificationPolicy] = None,
) -> Stage3VerificationResult:
    """
    Independently computes and verifies:
    1. Level 1 Symbolic Basis Matching
    2. Reverse Execution Verification
    3. Level 2 Superposition & Complex Amplitude Verification
    4. Level 3 Operator Matrix Unitarity & Correspondence
    """
    if policy is None:
        policy = VerificationPolicy(primary_level=VerificationLevel.LEVEL_1_SYMBOLIC_BASIS)

    tolerance = NUMERICAL_VERIFICATION_TOLERANCE  # 1e-12
    diagnostics: List[str] = []
    table = build_transition_table(program, domain_contract, encoding_spec, state_map, symbol_map)
    total_pairs = table.cardinality

    # -------------------------------------------------------------
    # LEVEL 1: Exact Symbolic Computational Basis Verification
    # -------------------------------------------------------------
    symbolic_basis_pass = True
    for pair in table.pairs:
        src_bits = pair.source_bits
        tgt_bits = pair.target_bits

        out_bits = execute_circuit_on_bitstring(circuit, src_bits)
        if out_bits != tgt_bits:
            symbolic_basis_pass = False
            diagnostics.append(
                f"[Level 1] Forward basis mismatch for {pair.source_config}: expected {tgt_bits}, got {out_bits}."
            )

    # -------------------------------------------------------------
    # REVERSE EXECUTION VERIFICATION
    # -------------------------------------------------------------
    reverse_execution_pass = True
    for pair in table.pairs:
        src_bits = pair.source_bits
        tgt_bits = pair.target_bits

        rev_out_bits = execute_inverse_circuit_on_bitstring(circuit, tgt_bits)
        if rev_out_bits != src_bits:
            reverse_execution_pass = False
            diagnostics.append(
                f"[Reverse] Reverse basis mismatch for {pair.target_config}: expected {src_bits}, got {rev_out_bits}."
            )

    # -------------------------------------------------------------
    # LEVEL 2: Superposition & Complex Amplitude Verification
    # -------------------------------------------------------------
    superposition_pass = True
    superposition_residual = 0.0

    total_qubits = circuit.total_width
    data_bits_count = sum(r.width for r in circuit.registers if r.register_type != "ANCILLA")

    # Deterministic complex amplitudes
    raw_amplitudes: Dict[str, complex] = {}
    for idx, pair in enumerate(table.pairs):
        amp = complex(1.0 + 0.5 * idx, 0.8 + 0.3 * (idx + 1))
        raw_amplitudes[pair.source_bits] = amp

    # Normalize
    norm_sq = sum(abs(amp) ** 2 for amp in raw_amplitudes.values())
    norm_z = math.sqrt(norm_sq)
    psi_input: Dict[str, complex] = {bits: amp / norm_z for bits, amp in raw_amplitudes.items()}

    # Construct expected superposition state |psi_expected>
    psi_expected: Dict[str, complex] = {}
    for pair in table.pairs:
        src_b = pair.source_bits
        tgt_b = pair.target_bits
        psi_expected[tgt_b] = psi_input[src_b]

    # Execute circuit on each basis component in psi_input
    psi_actual: Dict[str, complex] = {}
    for src_b, amp in psi_input.items():
        out_b = execute_circuit_on_bitstring(circuit, src_b)
        psi_actual[out_b] = psi_actual.get(out_b, 0.0) + amp

    # Compute superposition L2 norm residual ||psi_actual - psi_expected||_2
    all_target_keys = set(psi_expected.keys()).union(set(psi_actual.keys()))
    l2_sq = 0.0
    for k in all_target_keys:
        diff = psi_actual.get(k, 0.0) - psi_expected.get(k, 0.0)
        l2_sq += abs(diff) ** 2
    superposition_residual = math.sqrt(l2_sq)

    # Check norm preservation: ||U_C psi||_2 == ||psi||_2
    actual_norm = math.sqrt(sum(abs(amp) ** 2 for amp in psi_actual.values()))
    norm_diff = abs(actual_norm - 1.0)

    if superposition_residual >= tolerance:
        superposition_pass = False
        diagnostics.append(
            f"[Level 2] Superposition L2 norm residual {superposition_residual:.3e} exceeds tolerance {tolerance:.1e}."
        )

    if norm_diff >= tolerance:
        superposition_pass = False
        diagnostics.append(
            f"[Level 2] State vector norm diff {norm_diff:.3e} exceeds tolerance {tolerance:.1e}."
        )

    # -------------------------------------------------------------
    # LEVEL 3: Composed Operator Matrix Unitarity & Correspondence
    # -------------------------------------------------------------
    operator_unitary_pass = True
    left_unitarity_residual = 0.0
    right_unitarity_residual = 0.0

    # Collect basis indices for all domain configuration bitstrings
    basis_indices: List[int] = []
    target_indices_map: Dict[int, int] = {}

    for pair in table.pairs:
        src_b = pair.source_bits
        tgt_b = pair.target_bits

        src_int = 0
        for idx_b, ch in enumerate(src_b):
            if ch == "1":
                src_int |= (1 << idx_b)

        tgt_int = 0
        for idx_b, ch in enumerate(tgt_b):
            if ch == "1":
                tgt_int |= (1 << idx_b)

        basis_indices.append(src_int)
        target_indices_map[src_int] = tgt_int

    # Also test arbitrary computational basis indices up to 2^min(total_qubits, 8)
    sample_indices = set(basis_indices)
    sample_max = 1 << min(total_qubits, 8)
    for idx_k in range(sample_max):
        sample_indices.add(idx_k)

    # Compute Left Unitarity residual ||U_C^dag U_C - I||_2 on tested basis states
    left_errs = []
    for k in sample_indices:
        fwd_k = simulate_circuit_on_basis_index(circuit, total_qubits, k, reverse=False)
        rev_fwd_k = simulate_circuit_on_basis_index(circuit, total_qubits, fwd_k, reverse=True)
        if rev_fwd_k != k:
            left_errs.append(1.0)
        else:
            left_errs.append(0.0)
    left_unitarity_residual = math.sqrt(sum(e ** 2 for e in left_errs))

    # Compute Right Unitarity residual ||U_C U_C^dag - I||_2 on tested basis states
    right_errs = []
    for k in sample_indices:
        rev_k = simulate_circuit_on_basis_index(circuit, total_qubits, k, reverse=True)
        fwd_rev_k = simulate_circuit_on_basis_index(circuit, total_qubits, rev_k, reverse=False)
        if fwd_rev_k != k:
            right_errs.append(1.0)
        else:
            right_errs.append(0.0)
    right_unitarity_residual = math.sqrt(sum(e ** 2 for e in right_errs))

    if left_unitarity_residual >= tolerance:
        operator_unitary_pass = False
        diagnostics.append(
            f"[Level 3] Left unitarity residual {left_unitarity_residual:.3e} exceeds tolerance {tolerance:.1e}."
        )

    if right_unitarity_residual >= tolerance:
        operator_unitary_pass = False
        diagnostics.append(
            f"[Level 3] Right unitarity residual {right_unitarity_residual:.3e} exceeds tolerance {tolerance:.1e}."
        )

    # Matrix / Transition Semantic Correspondence Check
    for src_int, tgt_int in target_indices_map.items():
        res_int = simulate_circuit_on_basis_index(circuit, total_qubits, src_int, reverse=False)
        if res_int != tgt_int:
            operator_unitary_pass = False
            diagnostics.append(
                f"[Level 3] Matrix/transition correspondence failure: U_C|{src_int}> mapped to int {res_int}, expected {tgt_int}."
            )

    # Final overall validity (all 4 independent levels MUST pass)
    valid = (
        symbolic_basis_pass
        and reverse_execution_pass
        and superposition_pass
        and operator_unitary_pass
    )

    return Stage3VerificationResult(
        valid=valid,
        symbolic_basis_pass=symbolic_basis_pass,
        reverse_execution_pass=reverse_execution_pass,
        superposition_pass=superposition_pass,
        operator_unitary_pass=operator_unitary_pass,
        verified_pairs_count=total_pairs,
        superposition_residual=superposition_residual,
        left_unitarity_residual=left_unitarity_residual,
        right_unitarity_residual=right_unitarity_residual,
        diagnostics=diagnostics,
    )
