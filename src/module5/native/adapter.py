"""
Module 5 Stage 4 — Backend Adapter Abstraction Layer.

Defines the abstract base class BackendAdapter and the concrete ReferenceBackendAdapter.
Adapters handle physical-to-native gate resolution and vocabulary queries OFFLINE.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from src.module5.backend.model import BackendIdentity, BackendCapabilityModel, BackendType
from src.module5.backend.reference import create_reference_simulator_capabilities
from src.module5.physical_ir.model import PhysicalGateOperation
from src.module5.native.model import (
    NativeGateDefinition,
    NativeOperation,
    NativeResolutionStatus,
    NativeGateResolutionResult,
)
from src.module5.native.vocabulary import NativeGateVocabulary
from src.module5.native.registry import GateDecompositionRegistry


class BackendAdapter(ABC):
    """Abstract Base Class for Stage 4 Backend Adapters (Offline Translation Only)."""

    @abstractmethod
    def get_backend_identity(self) -> BackendIdentity:
        """Returns the identity metadata of the backend."""
        pass

    @abstractmethod
    def get_native_gate_vocabulary(self) -> Dict[str, NativeGateDefinition]:
        """Returns the supported native gate vocabulary."""
        pass

    @abstractmethod
    def resolve_gate(self, physical_gate: PhysicalGateOperation) -> NativeGateResolutionResult:
        """Resolves a PhysicalGateOperation into native operations or decomposition."""
        pass

    @abstractmethod
    def translate_gate(self, physical_gate: PhysicalGateOperation) -> List[NativeOperation]:
        """Translates a PhysicalGateOperation into native operations."""
        pass

    @abstractmethod
    def validate_native_operation(self, native_op: NativeOperation) -> bool:
        """Validates that a NativeOperation belongs to the native vocabulary."""
        pass

    @abstractmethod
    def get_translation_provenance(self) -> str:
        """Returns provenance identifier for the translation layer."""
        pass


class ReferenceBackendAdapter(BackendAdapter):
    """Concrete Reference Adapter based on Stage 2 reference_simulator capabilities."""

    def __init__(self, capability_model: Optional[BackendCapabilityModel] = None) -> None:
        if capability_model is None:
            self.model = create_reference_simulator_capabilities()
        else:
            self.model = capability_model

        self.vocabulary = NativeGateVocabulary.get_standard_vocabulary()

    def get_backend_identity(self) -> BackendIdentity:
        return self.model.identity

    def get_native_gate_vocabulary(self) -> Dict[str, NativeGateDefinition]:
        return self.vocabulary

    def validate_native_operation(self, native_op: NativeOperation) -> bool:
        gate_name = native_op.native_gate.upper()
        if gate_name not in self.vocabulary:
            return False
        gate_def = self.vocabulary[gate_name]
        return len(native_op.operands) == gate_def.arity and len(native_op.parameters) == gate_def.parameter_count

    def resolve_gate(self, physical_gate: PhysicalGateOperation) -> NativeGateResolutionResult:
        g_name = physical_gate.gate_type.upper()
        operands = physical_gate.control_nodes + (physical_gate.target_node,)

        # 1. Check if directly native on backend
        if g_name in self.vocabulary and self.model.supports_gate(g_name):
            native_op = NativeOperation(native_gate=g_name, operands=operands)
            return NativeGateResolutionResult(
                status=NativeResolutionStatus.DIRECT_NATIVE,
                source_gate=physical_gate,
                native_operations=[native_op],
            )

        # 2. Check for registered decomposition
        decomp = GateDecompositionRegistry.get_decomposition(g_name, self.model.identity.backend_id)
        if decomp is None:
            decomp = GateDecompositionRegistry.get_decomposition(g_name, "ALL")

        if decomp is not None:
            native_ops = decomp.decompose_func(physical_gate)
            # Verify all decomposed operations belong to native vocabulary
            for nop in native_ops:
                if not self.validate_native_operation(nop):
                    return NativeGateResolutionResult(
                        status=NativeResolutionStatus.UNSUPPORTED,
                        source_gate=physical_gate,
                        diagnostics=[f"Decomposition '{decomp.decomposition_id}' produced unsupported native operation '{nop.native_gate}'."],
                    )

            return NativeGateResolutionResult(
                status=NativeResolutionStatus.DECOMPOSED,
                source_gate=physical_gate,
                native_operations=native_ops,
                decomposition_id=decomp.decomposition_id,
            )

        # 3. Unsupported gate
        return NativeGateResolutionResult(
            status=NativeResolutionStatus.UNSUPPORTED,
            source_gate=physical_gate,
            diagnostics=[f"Gate '{physical_gate.gate_type}' is neither directly native nor decomposable on backend '{self.model.identity.backend_id}'."],
        )

    def translate_gate(self, physical_gate: PhysicalGateOperation) -> List[NativeOperation]:
        res = self.resolve_gate(physical_gate)
        if res.status == NativeResolutionStatus.UNSUPPORTED:
            raise ValueError(f"Translation failure: Unsupported gate '{physical_gate.gate_type}'. Diagnostics: {res.diagnostics}")
        return res.native_operations

    def get_translation_provenance(self) -> str:
        return "STAGE_4_HARDWARE_NATIVE_GATE_TRANSLATION::REFERENCE_ADAPTER"
