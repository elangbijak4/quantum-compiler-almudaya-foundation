"""
Module 6 Stage 4 — Level 3 Computational-Basis Semantic Equivalence Evaluator.

Verifies \forall x \in {0,1}^N: U(Q1)|x> \equiv U(Q2)|x>.
Full enumeration performed when 2^N <= exhaustive_basis_limit (default 1024).
"""

from typing import Tuple, Dict, Any, List
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module4.synthesis.verifier import execute_circuit_on_bitstring
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.mapping.correspondence import BasisCorrespondenceRecord


DEFAULT_EXHAUSTIVE_BASIS_LIMIT: int = 1024


class BasisEquivalenceEvaluator:
    """
    Evaluator for Level 3 Computational-Basis Semantic Equivalence.
    """

    @classmethod
    def verify_basis_equivalence(
        cls,
        model: ClassicalSemanticModel,
        circuit: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> Tuple[bool, List[BasisCorrespondenceRecord], List[str]]:
        """
        Stage 1 Level 3 Basis Equivalence Verification method.
        """
        records: List[BasisCorrespondenceRecord] = []
        diagnostics: List[str] = []
        all_pass = True

        bitstrings = sorted(list(model.transition_table.keys()))
        if not bitstrings and model.domain_contract:
            bitstrings = sorted([str(c) for c in model.domain_contract.domain])

        for idx, in_bits in enumerate(bitstrings):
            out_bits = execute_circuit_on_bitstring(circuit, in_bits)
            exp_target = model.transition_table.get(in_bits, in_bits)
            match = (out_bits[:len(exp_target)] == exp_target)
            cat = "HALTING" if (in_bits == exp_target) else "INITIAL"

            if not match:
                all_pass = False
                diagnostics.append(f"Basis mismatch for {in_bits}: got {out_bits}, expected {exp_target}")

            records.append(
                BasisCorrespondenceRecord(
                    index=idx,
                    config_id=f"CFG_{in_bits}",
                    config_category=cat,
                    encoded_input_bits=in_bits,
                    classical_successor_bits=exp_target,
                    quantum_output_bits=out_bits,
                    expected_output_bits=exp_target,
                    residual_l2=0.0 if match else 1.0,
                    passed=match,
                )
            )

        return all_pass, records, diagnostics

    @classmethod
    def evaluate_basis_equivalence(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        exhaustive_limit: int = DEFAULT_EXHAUSTIVE_BASIS_LIMIT,
        tolerance: float = 1e-12,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates Level 3 Computational-Basis Semantic Equivalence.
        Returns (is_equivalent, status_string, details).
        """
        qubits1 = sum(r.width for r in c1.registers)
        qubits2 = sum(r.width for r in c2.registers)

        if qubits1 != qubits2:
            details = {
                "qubit_mismatch": True,
                "qubit_count_1": qubits1,
                "qubit_count_2": qubits2,
                "basis_dimension": 0,
                "basis_states_tested": 0,
                "exhaustive": False,
                "exhaustive_basis_limit": exhaustive_limit,
            }
            return False, "BASIS_NON_EQUIVALENT", details

        num_qubits = qubits1
        total_basis_dim = 2 ** num_qubits
        is_exhaustive = (total_basis_dim <= exhaustive_limit)

        if is_exhaustive:
            states_to_test = range(total_basis_dim)
        else:
            # Deterministic sample up to exhaustive_limit
            states_to_test = range(min(total_basis_dim, exhaustive_limit))

        tested_count = len(states_to_test)
        equivalent_on_tested = True
        mismatched_state = -1

        for val in states_to_test:
            bitstr = format(val, f"0{num_qubits}b")
            out1 = execute_circuit_on_bitstring(c1, bitstr)
            out2 = execute_circuit_on_bitstring(c2, bitstr)

            if out1 != out2:
                equivalent_on_tested = False
                mismatched_state = val
                break

        details = {
            "num_qubits": num_qubits,
            "basis_dimension": total_basis_dim,
            "basis_states_tested": tested_count,
            "exhaustive": is_exhaustive,
            "exhaustive_basis_limit": exhaustive_limit,
            "equivalent_on_tested": equivalent_on_tested,
            "mismatched_state": mismatched_state,
        }

        if not equivalent_on_tested:
            status = "BASIS_NON_EQUIVALENT"
            is_eq = False
        elif is_exhaustive:
            status = "BASIS_EQUIVALENT"
            is_eq = True
        else:
            # Non-exhaustive sample, no mismatch found
            status = "BASIS_INCONCLUSIVE"
            is_eq = False

        return is_eq, status, details


# Alias for backward compatibility
Level3BasisVerifier = BasisEquivalenceEvaluator
