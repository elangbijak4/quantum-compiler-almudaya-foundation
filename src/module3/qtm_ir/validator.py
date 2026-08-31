"""
QTM-IR Semantic Validator (Module 3 Stage 5).

Provides observational, non-mutating validation across structural, semantic,
and mathematical invariant levels for QTM-IR models.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Any
import math

from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    QTM_IR_VERSION,
    CANONICAL_SEMANTIC_RELATION,
)


class DiagnosticCode(str, Enum):
    """Structured Diagnostic Codes for QTM-IR Validation."""
    QTM_SCHEMA_INVALID = "QTM_SCHEMA_INVALID"
    QTM_VERSION_UNSUPPORTED = "QTM_VERSION_UNSUPPORTED"
    QTM_BASIS_INVALID = "QTM_BASIS_INVALID"
    QTM_AMPLITUDE_INVALID = "QTM_AMPLITUDE_INVALID"
    QTM_DOMAIN_NOT_CLOSED = "QTM_DOMAIN_NOT_CLOSED"
    QTM_TRANSITION_NOT_BIJECTIVE = "QTM_TRANSITION_NOT_BIJECTIVE"
    QTM_MATRIX_NOT_SQUARE = "QTM_MATRIX_NOT_SQUARE"
    QTM_MATRIX_NOT_PERMUTATION = "QTM_MATRIX_NOT_PERMUTATION"
    QTM_MATRIX_NOT_UNITARY = "QTM_MATRIX_NOT_UNITARY"
    QTM_INITIAL_STATE_INVALID = "QTM_INITIAL_STATE_INVALID"
    QTM_TERMINAL_STATE_INVALID = "QTM_TERMINAL_STATE_INVALID"
    QTM_PROVENANCE_INVALID = "QTM_PROVENANCE_INVALID"


class ValidationSeverity(str, Enum):
    """Severity levels for validation diagnostics."""
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class ValidationDiagnostic:
    """Structured diagnostic reporting validation findings."""
    code: str
    path: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR


@dataclass
class ValidationResult:
    """Structured summary result returned by validate_qtm_ir."""
    valid: bool
    diagnostics: List[ValidationDiagnostic] = field(default_factory=list)

    def add_diagnostic(
        self, code: str, path: str, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> None:
        """Adds a diagnostic entry and marks valid = False if severity is ERROR."""
        self.diagnostics.append(ValidationDiagnostic(code=code, path=path, message=message, severity=severity))
        if severity == ValidationSeverity.ERROR:
            self.valid = False


def validate_qtm_ir(model: Any, tol: float = 1e-6) -> ValidationResult:
    """
    Observational, non-mutating validation of QTM-IR Model.

    Validates:
    - Level 1: Structural validation (model type, version, required attributes)
    - Level 2: Semantic validation (basis IDs, initial state references, terminal state consistency, provenance)
    - Level 3: Mathematical invariant validation (state norm == 1.0, total bijectivity, permutation structure, two-sided matrix unitarity)

    :param model: QTMIRModel instance to validate.
    :param tol: Numerical tolerance threshold.
    :return: ValidationResult instance.
    """
    result = ValidationResult(valid=True, diagnostics=[])

    # Level 1: Structural Validation
    if not isinstance(model, QTMIRModel):
        result.add_diagnostic(
            code=DiagnosticCode.QTM_SCHEMA_INVALID.value,
            path="root",
            message=f"Expected QTMIRModel instance, got {type(model).__name__}.",
        )
        return result

    if model.version != QTM_IR_VERSION:
        result.add_diagnostic(
            code=DiagnosticCode.QTM_VERSION_UNSUPPORTED.value,
            path="version",
            message=f"Unsupported QTM-IR schema version '{model.version}'. Expected '{QTM_IR_VERSION}'.",
        )

    if not model.machine_id or not isinstance(model.machine_id, str):
        result.add_diagnostic(
            code=DiagnosticCode.QTM_SCHEMA_INVALID.value,
            path="machine_id",
            message="machine_id must be a non-empty string.",
        )

    # Level 2: Basis States Validation
    if not model.basis_states or not isinstance(model.basis_states, dict):
        result.add_diagnostic(
            code=DiagnosticCode.QTM_BASIS_INVALID.value,
            path="basis_states",
            message="basis_states dictionary must not be empty.",
        )
    else:
        for b_id, b_state in model.basis_states.items():
            if not isinstance(b_state, QTMIRBasisState):
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_BASIS_INVALID.value,
                    path=f"basis_states['{b_id}']",
                    message=f"Expected QTMIRBasisState instance for key '{b_id}'.",
                )
            elif b_state.basis_id != b_id:
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_BASIS_INVALID.value,
                    path=f"basis_states['{b_id}'].basis_id",
                    message=f"Key '{b_id}' does not match basis_state.basis_id '{b_state.basis_id}'.",
                )

    # Level 2 & 3: Initial State Vector Validation
    v_init = model.initial_state_vector
    if not isinstance(v_init, QTMIRStateVector):
        result.add_diagnostic(
            code=DiagnosticCode.QTM_INITIAL_STATE_INVALID.value,
            path="initial_state_vector",
            message="initial_state_vector must be a QTMIRStateVector instance.",
        )
    elif not v_init.amplitudes:
        result.add_diagnostic(
            code=DiagnosticCode.QTM_INITIAL_STATE_INVALID.value,
            path="initial_state_vector.amplitudes",
            message="initial_state_vector amplitudes must not be empty.",
        )
    else:
        for ref_id, amp in v_init.amplitudes.items():
            if model.basis_states and ref_id not in model.basis_states:
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_INITIAL_STATE_INVALID.value,
                    path=f"initial_state_vector.amplitudes['{ref_id}']",
                    message=f"Referenced basis state ID '{ref_id}' not found in model.basis_states.",
                )

            if not isinstance(amp, QTMIRComplexNumber):
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_AMPLITUDE_INVALID.value,
                    path=f"initial_state_vector.amplitudes['{ref_id}']",
                    message=f"Amplitude for '{ref_id}' must be a QTMIRComplexNumber instance.",
                )
            elif math.isnan(amp.real) or math.isnan(amp.imag) or math.isinf(amp.real) or math.isinf(amp.imag):
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_AMPLITUDE_INVALID.value,
                    path=f"initial_state_vector.amplitudes['{ref_id}']",
                    message=f"Invalid complex amplitude value ({amp.real}, {amp.imag}) containing NaN or Inf.",
                )

        # Norm check
        norm = v_init.compute_norm()
        if abs(norm - 1.0) > tol:
            result.add_diagnostic(
                code=DiagnosticCode.QTM_AMPLITUDE_INVALID.value,
                path="initial_state_vector.norm",
                message=f"State vector norm preservation failure: ||ψ_0|| = {norm} != 1.0 (tolerance {tol}).",
            )

    # Level 2 & 3: Transition Mapping Validation (Correction C - Complete Forward & Reverse Total Bijection)
    t_map = model.transition_mapping
    if not isinstance(t_map, QTMIRTransitionMapping):
        result.add_diagnostic(
            code=DiagnosticCode.QTM_SCHEMA_INVALID.value,
            path="transition_mapping",
            message="transition_mapping must be a QTMIRTransitionMapping instance.",
        )
    elif model.basis_states:
        domain = set(model.basis_states.keys())
        f_map = t_map.forward_mapping
        r_map = t_map.reverse_mapping

        f_sources = set(f_map.keys())
        f_targets = set(f_map.values())

        # Check domain closure for forward sources & targets
        for src_id in f_sources:
            if src_id not in domain:
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_DOMAIN_NOT_CLOSED.value,
                    path=f"transition_mapping.forward_mapping['{src_id}']",
                    message=f"Forward source state '{src_id}' is not in basis_states domain D.",
                )
        for tgt_id in f_targets:
            if tgt_id not in domain:
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_DOMAIN_NOT_CLOSED.value,
                    path="transition_mapping.forward_mapping",
                    message=f"Forward target state '{tgt_id}' is not in basis_states domain D.",
                )

        # Check Forward Totality: dom(R_P) == D
        missing_f_sources = domain - f_sources
        if missing_f_sources:
            result.add_diagnostic(
                code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                path="transition_mapping.forward_mapping",
                message=f"Forward transition mapping is not total over domain D: missing outgoing transitions for {sorted(missing_f_sources)}.",
            )

        # Check Forward Surjectivity: ran(R_P) == D
        missing_f_targets = domain - f_targets
        if missing_f_targets:
            result.add_diagnostic(
                code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                path="transition_mapping.forward_mapping",
                message=f"Forward transition mapping is not surjective over domain D: states {sorted(missing_f_targets)} are never targets.",
            )

        # Check Forward Injectivity / Collision: len(f_sources) == len(f_targets)
        if len(f_sources) != len(f_targets):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                path="transition_mapping.forward_mapping",
                message=f"Forward mapping collision detected (not injective): Sources count ({len(f_sources)}) != Targets count ({len(f_targets)}).",
            )

        # Check Reverse Mapping Completeness (Correction C)
        if not r_map or not isinstance(r_map, dict):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                path="transition_mapping.reverse_mapping",
                message="reverse_mapping dictionary is missing or empty; compiler-produced QTM-IR must provide a complete reverse transition mapping.",
            )
        else:
            r_sources = set(r_map.keys())
            r_targets = set(r_map.values())

            for r_src in r_sources:
                if r_src not in domain:
                    result.add_diagnostic(
                        code=DiagnosticCode.QTM_DOMAIN_NOT_CLOSED.value,
                        path=f"transition_mapping.reverse_mapping['{r_src}']",
                        message=f"Reverse source state '{r_src}' is not in basis_states domain D.",
                    )
            for r_tgt in r_targets:
                if r_tgt not in domain:
                    result.add_diagnostic(
                        code=DiagnosticCode.QTM_DOMAIN_NOT_CLOSED.value,
                        path="transition_mapping.reverse_mapping",
                        message=f"Reverse target state '{r_tgt}' is not in basis_states domain D.",
                    )

            # Check Reverse Totality: dom(R_P^-1) == D
            missing_r_sources = domain - r_sources
            if missing_r_sources:
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                    path="transition_mapping.reverse_mapping",
                    message=f"Reverse transition mapping is not total over domain D: missing incoming transitions for {sorted(missing_r_sources)}.",
                )

            # Check Reverse Surjectivity: ran(R_P^-1) == D
            missing_r_targets = domain - r_targets
            if missing_r_targets:
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                    path="transition_mapping.reverse_mapping",
                    message=f"Reverse transition mapping is not surjective over domain D: states {sorted(missing_r_targets)} are never reverse targets.",
                )

            # Check Reverse Injectivity
            if len(r_sources) != len(r_targets):
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                    path="transition_mapping.reverse_mapping",
                    message=f"Reverse mapping collision detected (not injective): Sources count ({len(r_sources)}) != Targets count ({len(r_targets)}).",
                )

            # Check Both Composition Identities: R_P^-1 ∘ R_P = id_D AND R_P ∘ R_P^-1 = id_D
            for src_id in domain:
                if src_id in f_map:
                    tgt_id = f_map[src_id]
                    if r_map.get(tgt_id) != src_id:
                        result.add_diagnostic(
                            code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                            path=f"transition_mapping.reverse_mapping['{tgt_id}']",
                            message=f"Reverse composition identity failure (R_P^-1 ∘ R_P != id_D): R_P^-1(R_P('{src_id}')) = '{r_map.get(tgt_id)}' != '{src_id}'.",
                        )

            for tgt_id in domain:
                if tgt_id in r_map:
                    src_id = r_map[tgt_id]
                    if f_map.get(src_id) != tgt_id:
                        result.add_diagnostic(
                            code=DiagnosticCode.QTM_TRANSITION_NOT_BIJECTIVE.value,
                            path=f"transition_mapping.forward_mapping['{src_id}']",
                            message=f"Forward composition identity failure (R_P ∘ R_P^-1 != id_D): R_P(R_P^-1('{tgt_id}')) = '{f_map.get(src_id)}' != '{tgt_id}'.",
                        )

    # Level 2 & 3: Finite Matrix Representation Validation (Explicit Two-Sided Unitarity)
    mat_rep = model.matrix_representation
    if mat_rep is not None:
        if not isinstance(mat_rep, QTMIRMatrixRepresentation):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_SCHEMA_INVALID.value,
                path="matrix_representation",
                message="matrix_representation must be a QTMIRMatrixRepresentation instance.",
            )
        else:
            N = mat_rep.dimension
            if N != len(mat_rep.basis_order):
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_MATRIX_NOT_SQUARE.value,
                    path="matrix_representation.dimension",
                    message=f"Dimension {N} does not match basis_order length {len(mat_rep.basis_order)}.",
                )

            if len(mat_rep.matrix) != N or any(len(row) != N for row in mat_rep.matrix):
                result.add_diagnostic(
                    code=DiagnosticCode.QTM_MATRIX_NOT_SQUARE.value,
                    path="matrix_representation.matrix",
                    message=f"Matrix shape is not square {N}x{N}.",
                )
            else:
                # Permutation Matrix Check
                for i in range(N):
                    row_ones = sum(1 for c_val in mat_rep.matrix[i] if abs(c_val.real - 1.0) <= tol and abs(c_val.imag) <= tol)
                    row_zeros = sum(1 for c_val in mat_rep.matrix[i] if abs(c_val.real) <= tol and abs(c_val.imag) <= tol)
                    if row_ones != 1 or (row_ones + row_zeros) != N:
                        result.add_diagnostic(
                            code=DiagnosticCode.QTM_MATRIX_NOT_PERMUTATION.value,
                            path=f"matrix_representation.matrix[row {i}]",
                            message=f"Row {i} is not a valid permutation row (must have exactly one 1.0 entry).",
                        )

                for j in range(N):
                    col_ones = sum(1 for i in range(N) if abs(mat_rep.matrix[i][j].real - 1.0) <= tol and abs(mat_rep.matrix[i][j].imag) <= tol)
                    col_zeros = sum(1 for i in range(N) if abs(mat_rep.matrix[i][j].real) <= tol and abs(mat_rep.matrix[i][j].imag) <= tol)
                    if col_ones != 1 or (col_ones + col_zeros) != N:
                        result.add_diagnostic(
                            code=DiagnosticCode.QTM_MATRIX_NOT_PERMUTATION.value,
                            path=f"matrix_representation.matrix[col {j}]",
                            message=f"Column {j} is not a valid permutation column (must have exactly one 1.0 entry).",
                        )

                # Two-Sided Unitarity Check: [U_P]† [U_P] = I AND [U_P] [U_P]† = I
                # 1. Left Unitarity: [U_P]† [U_P] = I
                for i in range(N):
                    for j in range(N):
                        val_left = sum(
                            mat_rep.matrix[k][i].to_complex().conjugate() * mat_rep.matrix[k][j].to_complex()
                            for k in range(N)
                        )
                        expected = 1.0 if i == j else 0.0
                        if abs(val_left - expected) > tol:
                            result.add_diagnostic(
                                code=DiagnosticCode.QTM_MATRIX_NOT_UNITARY.value,
                                path=f"matrix_representation.matrix[[U_P]† [U_P] ({i},{j})]",
                                message=f"Left unitarity failure at ({i},{j}): computed {val_left} != expected {expected}.",
                            )

                # 2. Right Unitarity: [U_P] [U_P]† = I
                for i in range(N):
                    for j in range(N):
                        val_right = sum(
                            mat_rep.matrix[i][k].to_complex() * mat_rep.matrix[j][k].to_complex().conjugate()
                            for k in range(N)
                        )
                        expected = 1.0 if i == j else 0.0
                        if abs(val_right - expected) > tol:
                            result.add_diagnostic(
                                code=DiagnosticCode.QTM_MATRIX_NOT_UNITARY.value,
                                path=f"matrix_representation.matrix[[U_P] [U_P]† ({i},{j})]",
                                message=f"Right unitarity failure at ({i},{j}): computed {val_right} != expected {expected}.",
                            )

    # Level 2: Provenance Contract Validation (Correction B - Exact Canonical Semantic Relation Match)
    prov = model.provenance
    if prov is None:
        result.add_diagnostic(
            code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
            path="provenance",
            message="Missing required compiler provenance metadata.",
        )
    elif not isinstance(prov, QTMIRProvenance):
        result.add_diagnostic(
            code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
            path="provenance",
            message="provenance must be a QTMIRProvenance instance.",
        )
    else:
        if not prov.source_rutm_program_hash or not isinstance(prov.source_rutm_program_hash, str):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
                path="provenance.source_rutm_program_hash",
                message="source_rutm_program_hash must be a non-empty string.",
            )

        if not prov.source_module or not isinstance(prov.source_module, str):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
                path="provenance.source_module",
                message="source_module must be a non-empty string.",
            )

        if not prov.stage or not isinstance(prov.stage, str):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
                path="provenance.stage",
                message="stage must be a non-empty string.",
            )

        if not prov.compiler_version or not isinstance(prov.compiler_version, str):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
                path="provenance.compiler_version",
                message="compiler_version must be a non-empty string.",
            )

        if not prov.semantic_relation or not isinstance(prov.semantic_relation, str):
            result.add_diagnostic(
                code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
                path="provenance.semantic_relation",
                message="semantic_relation must be a non-empty string.",
            )
        elif prov.semantic_relation != CANONICAL_SEMANTIC_RELATION:
            result.add_diagnostic(
                code=DiagnosticCode.QTM_PROVENANCE_INVALID.value,
                path="provenance.semantic_relation",
                message=f"semantic_relation '{prov.semantic_relation}' does not match canonical relation '{CANONICAL_SEMANTIC_RELATION}' exactly.",
            )

    return result
