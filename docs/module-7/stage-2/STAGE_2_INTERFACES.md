# MODULE 7 STAGE 2 — INTERFACE SPECIFICATION

## 1. Data Contract Definitions

```python
@dataclass(frozen=True)
class LoweringPolicy:
    policy_id: str
    decomposition_strategy: str = "EXACT_DECOMPOSITION"
    qubit_mapping_strategy: str = "NAIVE_DIRECT"
    routing_strategy: str = "LOOKAHEAD_SWAP"
    allow_ancilla: bool = False
    max_ancilla_count: int = 0
    optimization_level: int = 0
    policy_hash: str = ""


@dataclass(frozen=True)
class NativeCircuitArtifact:
    native_circuit_id: str
    backend_id: str
    capability_hash: str
    native_gate_sequence: Tuple[Dict[str, Any], ...]
    qubit_mapping: Dict[int, int]
    native_gate_count: int
    circuit_depth: int
    inserted_swap_count: int
    native_circuit_hash: str = ""


@dataclass(frozen=True)
class LoweringResultArtifact:
    lowering_id: str
    logical_circuit_id: str
    logical_circuit_hash: str
    backend_id: str
    capability_version: str
    capability_hash: str
    policy_hash: str
    status: LoweringStatus
    native_circuit: Optional[NativeCircuitArtifact]
    qubit_mapping: Dict[int, int]
    semantic_verification_status: str
    semantic_verification_reference: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    lowering_hash: str = ""
```

---

## 2. Lowering Protocol Definitions

```python
class LoweringEngineProtocol(Protocol):
    def lower_circuit(
        self,
        logical_circuit_id: str,
        logical_circuit_hash: str,
        backend_capability: BackendCapabilityModel,
        policy: LoweringPolicy,
    ) -> LoweringResultArtifact:
        ...


class SemanticVerificationAdapterProtocol(Protocol):
    def verify_equivalence(
        self,
        logical_circuit_hash: str,
        native_circuit_hash: str,
    ) -> str:
        ...
```
