# MODULE 7 STAGE 3 — INTERFACE SPECIFICATION

## 1. Data Contract Definitions

```python
@dataclass(frozen=True)
class SimulatorConfig:
    config_id: str
    execution_mode: str = "STATEVECTOR_EXACT"
    shots: int = 1000
    seed_prng: Optional[int] = 42
    max_qubits: int = 32
    precision: str = "COMPLEX128"
    config_hash: str = ""


@dataclass(frozen=True)
class ReferenceStatevectorSummary:
    qubit_count: int
    probabilities: Dict[str, float]
    statevector_hash: str = ""


@dataclass(frozen=True)
class SimulatorJobResult:
    job_id: str
    native_circuit_id: str
    native_circuit_hash: str
    backend_id: str
    capability_hash: str
    lowering_id: str
    status: SimulationExecutionStatus
    shots: int
    measurement_counts: Dict[str, int]
    measurement_distribution: Dict[str, float]
    statevector_summary: Optional[ReferenceStatevectorSummary] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    job_hash: str = ""
```

---

## 2. Reference Simulator Protocol Definition

```python
class ReferenceSimulatorProtocol(Protocol):
    def execute_lowered_circuit(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
        config: SimulatorConfig,
    ) -> SimulatorJobResult:
        ...
```
