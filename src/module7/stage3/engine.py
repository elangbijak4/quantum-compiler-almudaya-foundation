"""
Module 7 Stage 3 — Local Reference Simulator Engine Implementation.

Provides LocalReferenceSimulatorEngine implementing ReferenceSimulatorProtocol.
Performs pre-execution validation, ideal statevector evolution, computational basis measurement,
deterministic shot sampling, and immutable result construction.
"""

from typing import Dict, Any, Optional
import uuid

from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import LoweringStatus, LoweringResultArtifact
from src.module7.stage3.model import (
    SimulationExecutionStatus,
    SimulatorConfig,
    ReferenceStatevectorSummary,
    SimulatorJobResult,
)
from src.module7.stage3.interfaces import ReferenceSimulatorProtocol
from src.module7.stage3.statevector import LocalReferenceStatevectorSimulator
from src.module7.stage3.sampling import DeterministicShotSampler


class LocalReferenceSimulatorEngine(ReferenceSimulatorProtocol):
    """
    Module 7 Stage 3 Production Engine.
    
    Executes semantically verified native quantum circuits on local ideal reference simulator.
    """

    DEFAULT_SHOTS = 1000
    MAX_QUBITS = 32
    MAX_SHOTS = 1000000
    MAX_DEPTH = 10000

    def execute_lowered_circuit(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
        config: Optional[SimulatorConfig] = None,
    ) -> SimulatorJobResult:
        """
        Executes a semantically verified lowered native circuit on local reference simulator.
        """
        if config is None:
            config = SimulatorConfig(
                config_id=f"CFG_{uuid.uuid4().hex[:8].upper()}",
                shots=self.DEFAULT_SHOTS,
            )

        job_id = f"JOB_SIM_{uuid.uuid4().hex[:8].upper()}"

        # 1. Eligibility Check: Lowering status MUST be SEMANTICALLY_VERIFIED
        if lowering_result.status != LoweringStatus.SEMANTICALLY_VERIFIED:
            return SimulatorJobResult(
                job_id=job_id,
                native_circuit_id=lowering_result.native_circuit.native_circuit_id if lowering_result.native_circuit else "",
                native_circuit_hash=lowering_result.native_circuit.native_circuit_hash if lowering_result.native_circuit else "",
                backend_id=backend_capability.backend_id,
                capability_hash=backend_capability.capability_hash,
                lowering_id=lowering_result.lowering_id,
                status=SimulationExecutionStatus.REJECTED,
                shots=config.shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "rejection_reason": "EXECUTION_INPUT_INVALID: Circuit lowering status is not SEMANTICALLY_VERIFIED.",
                    "lowering_status": lowering_result.status.value,
                },
            )

        if not lowering_result.native_circuit:
            return SimulatorJobResult(
                job_id=job_id,
                native_circuit_id="",
                native_circuit_hash="",
                backend_id=backend_capability.backend_id,
                capability_hash=backend_capability.capability_hash,
                lowering_id=lowering_result.lowering_id,
                status=SimulationExecutionStatus.REJECTED,
                shots=config.shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "rejection_reason": "EXECUTION_INPUT_INVALID: Missing NativeCircuitArtifact in lowering result.",
                },
            )

        native_circuit = lowering_result.native_circuit
        gate_seq = native_circuit.native_gate_sequence

        # Determine qubit count from max physical qubit index referenced in operations or qubit_mapping
        max_q = 0
        if native_circuit.qubit_mapping:
            max_q = max(native_circuit.qubit_mapping.values()) + 1
        for op in gate_seq:
            for q in op.get("qubits", ()):
                if q + 1 > max_q:
                    max_q = q + 1
        if max_q == 0:
            max_q = 1

        # 2. Resource Limit Check: Qubits, Depth, Shots
        if max_q > self.MAX_QUBITS or max_q > backend_capability.qubit_count:
            return SimulatorJobResult(
                job_id=job_id,
                native_circuit_id=native_circuit.native_circuit_id,
                native_circuit_hash=native_circuit.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                capability_hash=backend_capability.capability_hash,
                lowering_id=lowering_result.lowering_id,
                status=SimulationExecutionStatus.REJECTED,
                shots=config.shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "rejection_reason": f"EXECUTION_RESOURCE_EXHAUSTED: Qubit count {max_q} exceeds limit.",
                },
            )

        if len(gate_seq) > self.MAX_DEPTH:
            return SimulatorJobResult(
                job_id=job_id,
                native_circuit_id=native_circuit.native_circuit_id,
                native_circuit_hash=native_circuit.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                capability_hash=backend_capability.capability_hash,
                lowering_id=lowering_result.lowering_id,
                status=SimulationExecutionStatus.REJECTED,
                shots=config.shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "rejection_reason": f"EXECUTION_RESOURCE_EXHAUSTED: Circuit depth {len(gate_seq)} exceeds MAX_DEPTH {self.MAX_DEPTH}.",
                },
            )

        if config.shots < 1 or config.shots > self.MAX_SHOTS:
            return SimulatorJobResult(
                job_id=job_id,
                native_circuit_id=native_circuit.native_circuit_id,
                native_circuit_hash=native_circuit.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                capability_hash=backend_capability.capability_hash,
                lowering_id=lowering_result.lowering_id,
                status=SimulationExecutionStatus.REJECTED,
                shots=config.shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "rejection_reason": f"EXECUTION_RESOURCE_EXHAUSTED: Shot count {config.shots} invalid (must be 1..{self.MAX_SHOTS}).",
                },
            )

        # 3. Native Gate Containment Validation
        for op in gate_seq:
            gate_name = op["gate"]
            if gate_name not in backend_capability.native_gate_set:
                return SimulatorJobResult(
                    job_id=job_id,
                    native_circuit_id=native_circuit.native_circuit_id,
                    native_circuit_hash=native_circuit.native_circuit_hash,
                    backend_id=backend_capability.backend_id,
                    capability_hash=backend_capability.capability_hash,
                    lowering_id=lowering_result.lowering_id,
                    status=SimulationExecutionStatus.FAILED,
                    shots=config.shots,
                    measurement_counts={},
                    measurement_distribution={},
                    provenance={
                        "failure_reason": f"BACKEND_CAPABILITY_MISMATCH: Gate '{gate_name}' not supported by backend native_gate_set.",
                    },
                )

        # 4. Execute Statevector Evolution
        try:
            simulator = LocalReferenceStatevectorSimulator(num_qubits=max_q)
            simulator.execute_gate_sequence(gate_seq)
            exact_probs = simulator.get_probabilities()
            statevector_summary = simulator.get_statevector_summary()
        except Exception as err:
            return SimulatorJobResult(
                job_id=job_id,
                native_circuit_id=native_circuit.native_circuit_id,
                native_circuit_hash=native_circuit.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                capability_hash=backend_capability.capability_hash,
                lowering_id=lowering_result.lowering_id,
                status=SimulationExecutionStatus.FAILED,
                shots=config.shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "failure_reason": f"STATE_EVOLUTION_FAILURE: {str(err)}",
                },
            )

        # 5. Execute Shot Sampling / Exact Distribution Construction
        seed_used = config.seed_prng if config.seed_prng is not None else 42
        sampler = DeterministicShotSampler(seed_prng=seed_used)
        counts, sampled_dist = sampler.sample_shots(exact_probs, config.shots)

        provenance = {
            "execution_id": job_id,
            "native_circuit_hash": native_circuit.native_circuit_hash,
            "backend_id": backend_capability.backend_id,
            "capability_hash": backend_capability.capability_hash,
            "lowering_id": lowering_result.lowering_id,
            "execution_mode": config.execution_mode,
            "shots": config.shots,
            "seed_prng": seed_used,
            "simulator_version": "1.0.0-LOCAL_REFERENCE",
            "config_hash": config.config_hash,
        }

        return SimulatorJobResult(
            job_id=job_id,
            native_circuit_id=native_circuit.native_circuit_id,
            native_circuit_hash=native_circuit.native_circuit_hash,
            backend_id=backend_capability.backend_id,
            capability_hash=backend_capability.capability_hash,
            lowering_id=lowering_result.lowering_id,
            status=SimulationExecutionStatus.COMPLETED,
            shots=config.shots,
            measurement_counts=counts,
            measurement_distribution=sampled_dist,
            statevector_summary=statevector_summary,
            provenance=provenance,
        )
