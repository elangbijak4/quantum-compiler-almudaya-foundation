"""
Module 5 Stage 4 — Main Hardware Native Gate Translator Engine.

Transforms a physicalized PhysicalCircuitIR into a backend-native NativeCircuitIR OFFLINE.
"""

from typing import List, Optional
from src.module5.physical_ir.model import PhysicalCircuitIR, PhysicalGateOperation, ExecutionProvenance
from src.module5.physical_ir.validator import validate_physical_circuit_ir
from src.module5.native.model import (
    NativeOperation,
    NativeCircuitIR,
    NativeTranslationResult,
    NativeResolutionStatus,
    SCHEMA_VERSION,
)
from src.module5.native.adapter import BackendAdapter
from src.module5.native.validator import validate_native_circuit_ir
from src.module5.native.verifier import NativeCircuitVerifier


class NativeTranslator:
    """Primary Stage 4 Native Gate Translator Engine (Offline Translation Only)."""

    @classmethod
    def translate(
        cls,
        physical_circuit: PhysicalCircuitIR,
        adapter: BackendAdapter,
    ) -> NativeTranslationResult:
        """
        Translates a PhysicalCircuitIR into a NativeCircuitIR for the target backend adapter.
        
        Guarantees:
        1. Fully offline translation (NO hardware execution).
        2. Native vocabulary closure (all gates belong to adapter vocabulary).
        3. Strict 3-level semantic equivalence verification (residual < 10^-12).
        4. Upstream provenance preservation.
        """
        diagnostics: List[str] = []

        # 1. Validate physical_circuit
        phys_val = validate_physical_circuit_ir(physical_circuit)
        if not phys_val.valid:
            return NativeTranslationResult(
                success=False,
                source_circuit_id=physical_circuit.physical_circuit_id,
                native_circuit_id="",
                backend_id=adapter.get_backend_identity().backend_id,
                diagnostics=[f"Input PhysicalCircuitIR is invalid: {phys_val.errors}"],
            )

        backend_id = adapter.get_backend_identity().backend_id
        backend_ver = adapter.get_backend_identity().backend_version

        native_ops: List[NativeOperation] = []
        unresolved: List[PhysicalGateOperation] = []
        decomp_records: List[str] = []
        op_counter = 0

        # 2. Translate physical gates
        for g_idx, phys_gate in enumerate(physical_circuit.gates):
            res = adapter.resolve_gate(phys_gate)

            if res.status == NativeResolutionStatus.UNSUPPORTED:
                unresolved.append(phys_gate)
                diagnostics.extend(res.diagnostics)
            else:
                if res.decomposition_id:
                    decomp_records.append(f"Op {phys_gate.operation_index} ({phys_gate.gate_type}) -> Decomposed via {res.decomposition_id}")

                for nop in res.native_operations:
                    translated_nop = NativeOperation(
                        native_gate=nop.native_gate,
                        operands=nop.operands,
                        parameters=nop.parameters,
                        operation_index=op_counter,
                    )
                    native_ops.append(translated_nop)
                    op_counter += 1

        if unresolved:
            return NativeTranslationResult(
                success=False,
                source_circuit_id=physical_circuit.physical_circuit_id,
                native_circuit_id="",
                backend_id=backend_id,
                unresolved_operations=unresolved,
                decomposition_records=decomp_records,
                diagnostics=diagnostics,
            )

        # 3. Construct NativeCircuitIR
        native_circuit_id = f"native_{physical_circuit.physical_circuit_id}"
        rutm_hash = physical_circuit.provenance.source_rutm_program_hash if physical_circuit.provenance else "rutm_hash_unknown"
        qtm_id = physical_circuit.provenance.source_qtm_machine_id if physical_circuit.provenance else "qtm_id_unknown"

        provenance = ExecutionProvenance(
            source_rutm_program_hash=rutm_hash,
            source_qtm_machine_id=qtm_id,
            logical_circuit_id=physical_circuit.source_logical_circuit_id,
            physical_circuit_id=physical_circuit.physical_circuit_id,
            backend_id=backend_id,
            compiler_version="0.5.0-alpha",
        )

        qubit_ids = [pq.node_id for pq in physical_circuit.physical_qubits]

        native_circuit = NativeCircuitIR(
            circuit_id=native_circuit_id,
            backend_id=backend_id,
            backend_version=backend_ver,
            qubits=qubit_ids,
            native_operations=native_ops,
            input_mapping=physical_circuit.mapping,
            output_mapping=physical_circuit.mapping,
            provenance=provenance,
            schema_version=SCHEMA_VERSION,
        )

        # 4. Validate NativeCircuitIR
        nat_val = validate_native_circuit_ir(native_circuit, adapter)
        if not nat_val.valid:
            return NativeTranslationResult(
                success=False,
                source_circuit_id=physical_circuit.physical_circuit_id,
                native_circuit_id=native_circuit_id,
                backend_id=backend_id,
                native_circuit=native_circuit,
                diagnostics=[f"NativeCircuitIR validation failed: {nat_val.errors}"],
            )

        # 5. Semantic Equivalence & Unitarity Verification
        ver_rep = NativeCircuitVerifier.verify_equivalence(physical_circuit, native_circuit)
        if not ver_rep.verified:
            return NativeTranslationResult(
                success=False,
                source_circuit_id=physical_circuit.physical_circuit_id,
                native_circuit_id=native_circuit_id,
                backend_id=backend_id,
                native_circuit=native_circuit,
                semantic_verification=False,
                diagnostics=[f"Semantic equivalence verification failed: {ver_rep.errors}"],
            )

        return NativeTranslationResult(
            success=True,
            source_circuit_id=physical_circuit.physical_circuit_id,
            native_circuit_id=native_circuit_id,
            backend_id=backend_id,
            native_circuit=native_circuit,
            translated_operations_count=len(native_ops),
            decomposition_records=decomp_records,
            semantic_verification=True,
            provenance=provenance,
            diagnostics=[],
        )
