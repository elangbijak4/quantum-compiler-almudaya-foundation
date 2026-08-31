"""
Module 6 Stage 1 — Master Semantic Verification Entrypoint.

Orchestrates Stage 1 Level 3 basis equivalence and Level 5 operator equivalence verification,
returning a structured, deterministic SemanticEquivalenceReport.
"""

from typing import List, Optional
import hashlib
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module4.circuit_ir.validator import validate_circuit_ir
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.equivalence.basis import Level3BasisVerifier
from src.module6.equivalence.operator import Level5OperatorVerifier
from src.module6.equivalence.report import (
    SemanticEquivalenceReport,
    EquivalenceStatus,
    FailureCode,
)


class Stage1SemanticVerifier:
    """
    Master Verifier for Module 6 Stage 1 Formal Semantic Mapping & Equivalence Analysis.
    """

    @classmethod
    def verify_semantic_equivalence(
        cls,
        model: ClassicalSemanticModel,
        circuit: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> SemanticEquivalenceReport:
        """
        Executes full Stage 1 verification of classical semantic model A against logical circuit F(A).
        """
        diagnostics: List[str] = []

        # 1. Validate Classical Semantic Model
        if not model.domain_contract.domain or not model.transition_table:
            return SemanticEquivalenceReport(
                classical_algorithm_id=model.algorithm_id,
                classical_domain_size=len(model.domain_contract.domain),
                logical_circuit_id=circuit.circuit_id if circuit else "NONE",
                status=EquivalenceStatus.FAILED,
                level_3_status=EquivalenceStatus.FAILED,
                level_5_status=EquivalenceStatus.FAILED,
                failure_code=FailureCode.INVALID_CLASSICAL_SEMANTIC_MODEL,
                failure_message="Classical semantic model domain is empty or missing transition table.",
                diagnostics=["Classical model is invalid or empty."],
            )

        # 2. Validate Quantum Circuit IR
        if circuit is None:
            return SemanticEquivalenceReport(
                classical_algorithm_id=model.algorithm_id,
                classical_domain_size=len(model.domain_contract.domain),
                logical_circuit_id="NONE",
                status=EquivalenceStatus.FAILED,
                level_3_status=EquivalenceStatus.FAILED,
                level_5_status=EquivalenceStatus.FAILED,
                failure_code=FailureCode.INVALID_QUANTUM_CIRCUIT,
                failure_message="QuantumCircuitIR is None.",
                diagnostics=["QuantumCircuitIR is None."],
            )

        val_res = validate_circuit_ir(circuit)
        if not val_res.valid:
            return SemanticEquivalenceReport(
                classical_algorithm_id=model.algorithm_id,
                classical_domain_size=len(model.domain_contract.domain),
                logical_circuit_id=circuit.circuit_id,
                status=EquivalenceStatus.FAILED,
                level_3_status=EquivalenceStatus.FAILED,
                level_5_status=EquivalenceStatus.FAILED,
                failure_code=FailureCode.INVALID_QUANTUM_CIRCUIT,
                failure_message=f"QuantumCircuitIR validation failed: {val_res.errors}",
                diagnostics=val_res.errors,
            )

        # 3. Level 3 Basis Equivalence Verification
        l3_pass, basis_records, l3_diags = Level3BasisVerifier.verify_basis_equivalence(
            model=model, circuit=circuit, tolerance=tolerance
        )
        diagnostics.extend(l3_diags)

        level_3_status = EquivalenceStatus.VERIFIED if l3_pass else EquivalenceStatus.FAILED

        # 4. Level 5 Operator Equivalence Verification
        (
            l5_pass,
            op_residual,
            left_u_res,
            right_u_res,
            superpos_res,
            ancilla_pass,
            phase_pass,
            reverse_pass,
            l5_diags,
        ) = Level5OperatorVerifier.verify_operator_equivalence(
            model=model, circuit=circuit, tolerance=tolerance
        )
        diagnostics.extend(l5_diags)

        level_5_status = EquivalenceStatus.VERIFIED if l5_pass else EquivalenceStatus.FAILED

        # Determine Master Status & Failure Code
        overall_pass = l3_pass and l5_pass
        master_status = EquivalenceStatus.VERIFIED if overall_pass else EquivalenceStatus.FAILED

        failure_code: Optional[FailureCode] = None
        failure_msg: Optional[str] = None

        if not ancilla_pass:
            failure_code = FailureCode.ANCILLA_CLEANLINESS_FAILURE
            failure_msg = "Ancilla cleanliness verification failed (dirty ancilla detected)."
        elif not l3_pass:
            failure_code = FailureCode.BASIS_EQUIVALENCE_FAILURE
            failure_msg = "Level 3 Basis-state equivalence failed."
        elif not l5_pass:
            failure_code = FailureCode.OPERATOR_EQUIVALENCE_FAILURE
            failure_msg = "Level 5 Operator equivalence or unitarity failed."

        # Provenance
        provenance = {
            "source_program_hash": model.source_program_hash,
            "classical_model_id": model.algorithm_id,
            "logical_circuit_id": circuit.circuit_id,
            "compiler_version": "1.0.0",
            "module6_stage1_version": "1.0.0",
            "tolerance": str(tolerance),
        }

        # Deterministic Analysis ID
        raw_det = f"{model.compute_deterministic_id()}|{circuit.circuit_id}|{master_status.value}"
        det_id = hashlib.sha256(raw_det.encode("utf-8")).hexdigest()

        return SemanticEquivalenceReport(
            classical_algorithm_id=model.algorithm_id,
            classical_domain_size=len(model.domain_contract.domain),
            logical_circuit_id=circuit.circuit_id,
            status=master_status,
            level_3_status=level_3_status,
            level_5_status=level_5_status,
            failure_code=failure_code,
            failure_message=failure_msg,
            basis_results=basis_records,
            operator_residual=op_residual,
            left_unitarity_residual=left_u_res,
            right_unitarity_residual=right_u_res,
            superposition_residual=superpos_res,
            ancilla_cleanliness_pass=ancilla_pass,
            global_phase_pass=phase_pass,
            reverse_equivalence_pass=reverse_pass,
            provenance=provenance,
            deterministic_analysis_id=det_id,
            diagnostics=diagnostics,
        )
