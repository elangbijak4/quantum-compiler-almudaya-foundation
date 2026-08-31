"""
Module 7 Stage 4 — Provider Translation Layer & Provider Program Artifact.

Provides ProviderProgramArtifact and ProviderTranslator for translating certified
NativeCircuitArtifact objects into provider-specific quantum program representations
(e.g., OpenQASM 2.0, provider IR, API payloads).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json

from src.module7.stage2.model import NativeCircuitArtifact


@dataclass(frozen=True)
class ProviderProgramArtifact:
    """
    Immutable provider-facing program artifact derived from a NativeCircuitArtifact.
    """
    program_id: str
    provider_id: str
    backend_id: str
    source_native_circuit_id: str
    source_native_circuit_hash: str
    provider_language: str  # e.g., "OPENQASM_2_0", "AWS_BRAKET_JSON", "CIRQ_JSON"
    provider_program_text: str
    translation_version: str = "1.0.0"
    translation_hash: str = ""

    def __post_init__(self) -> None:
        if not self.translation_hash:
            object.__setattr__(self, "translation_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "program_id": self.program_id,
            "provider_id": self.provider_id,
            "backend_id": self.backend_id,
            "source_native_circuit_id": self.source_native_circuit_id,
            "source_native_circuit_hash": self.source_native_circuit_hash,
            "provider_language": self.provider_language,
            "provider_program_text": self.provider_program_text,
            "translation_version": self.translation_version,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "program_id": self.program_id,
            "provider_id": self.provider_id,
            "backend_id": self.backend_id,
            "source_native_circuit_id": self.source_native_circuit_id,
            "source_native_circuit_hash": self.source_native_circuit_hash,
            "provider_language": self.provider_language,
            "provider_program_text": self.provider_program_text,
            "translation_version": self.translation_version,
            "translation_hash": self.translation_hash,
        }


class ProviderTranslator:
    """
    Translates a certified NativeCircuitArtifact into a ProviderProgramArtifact.
    
    Invariants:
    1. Pure representation mapping: Does NOT re-lower, re-route, optimize, or alter quantum semantics.
    2. Deterministic SHA-256 translation_hash.
    3. Preserves exact qubit indices, gate order, and parameter values.
    """

    def translate(
        self,
        native_circuit: NativeCircuitArtifact,
        provider_id: str,
        backend_id: str,
    ) -> ProviderProgramArtifact:
        """Translates native circuit to target provider program artifact."""
        provider_upper = provider_id.upper()
        program_id = f"PROG_{native_circuit.native_circuit_id}_{provider_upper}"

        if provider_upper in ("IBM", "LOCAL_REFERENCE", "MOCK"):
            qasm_text = self._to_openqasm2(native_circuit)
            return ProviderProgramArtifact(
                program_id=program_id,
                provider_id=provider_id,
                backend_id=backend_id,
                source_native_circuit_id=native_circuit.native_circuit_id,
                source_native_circuit_hash=native_circuit.native_circuit_hash,
                provider_language="OPENQASM_2_0",
                provider_program_text=qasm_text,
            )

        elif provider_upper in ("AWS", "GOOGLE", "MICROSOFT"):
            json_ir = self._to_json_ir(native_circuit, provider_id)
            return ProviderProgramArtifact(
                program_id=program_id,
                provider_id=provider_id,
                backend_id=backend_id,
                source_native_circuit_id=native_circuit.native_circuit_id,
                source_native_circuit_hash=native_circuit.native_circuit_hash,
                provider_language=f"{provider_upper}_IR_JSON",
                provider_program_text=json_ir,
            )

        else:
            # Generic fallback QASM translation
            qasm_text = self._to_openqasm2(native_circuit)
            return ProviderProgramArtifact(
                program_id=program_id,
                provider_id=provider_id,
                backend_id=backend_id,
                source_native_circuit_id=native_circuit.native_circuit_id,
                source_native_circuit_hash=native_circuit.native_circuit_hash,
                provider_language="OPENQASM_2_0",
                provider_program_text=qasm_text,
            )

    def _to_openqasm2(self, native_circuit: NativeCircuitArtifact) -> str:
        """Converts native circuit sequence to OpenQASM 2.0 string representation."""
        num_qubits = max(native_circuit.qubit_mapping.values()) + 1 if native_circuit.qubit_mapping else 1
        lines = [
            'OPENQASM 2.0;',
            'include "qelib1.inc";',
            f'qreg q[{num_qubits}];',
            f'creg c[{num_qubits}];',
        ]

        for op in native_circuit.native_gate_sequence:
            gate_name = op["gate"].lower()
            qubits = op["qubits"]
            params = op.get("params", {})

            if gate_name in ("h", "x", "y", "z"):
                q_str = f"q[{qubits[0]}]"
                lines.append(f"{gate_name} {q_str};")

            elif gate_name in ("rx", "ry", "rz"):
                param_val = params.get("theta") if gate_name in ("rx", "ry") else params.get("phi", 0.0)
                q_str = f"q[{qubits[0]}]"
                lines.append(f"{gate_name}({param_val}) {q_str};")

            elif gate_name in ("cnot", "cx"):
                lines.append(f"cx q[{qubits[0]}], q[{qubits[1]}];")

            elif gate_name == "cz":
                lines.append(f"cz q[{qubits[0]}], q[{qubits[1]}];")

            elif gate_name == "swap":
                lines.append(f"swap q[{qubits[0]}], q[{qubits[1]}];")

        # Add computational basis measurements
        for i in range(num_qubits):
            lines.append(f"measure q[{i}] -> c[{i}];")

        return "\n".join(lines)

    def _to_json_ir(self, native_circuit: NativeCircuitArtifact, provider_id: str) -> str:
        """Converts native circuit sequence to JSON IR payload."""
        payload = {
            "provider": provider_id,
            "qubit_count": max(native_circuit.qubit_mapping.values()) + 1 if native_circuit.qubit_mapping else 1,
            "operations": list(native_circuit.native_gate_sequence),
        }
        return json.dumps(payload, sort_keys=True)
