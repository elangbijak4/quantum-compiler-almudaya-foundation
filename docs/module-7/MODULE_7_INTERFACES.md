# MODULE 7 — INTERFACE SPECIFICATIONS

## 1. Primary Data Contracts

- `BackendCapabilityModel`: Represents target device native gates, qubit count, topology map, max shots, and capability version.
- `LoweringResult`: Represents native gate sequence, qubit placement mapping, lowering ID, and equivalence preservation status.
- `ExecutionJobResult`: Represents job ID, backend ID, status, shot count, measurement distribution, and execution provenance.
- `CredentialReference`: Non-sensitive credential identifier (`credential_ref: "env:..."`).

---

## 2. Protocol Interfaces

```python
class BackendRegistryProtocol(Protocol):
    def register_backend(self, capability: BackendCapabilityModel) -> None: ...
    def get_backend(self, backend_id: str) -> Optional[BackendCapabilityModel]: ...
    def list_backends(self) -> Tuple[BackendCapabilityModel, ...]: ...

class LoweringEngineProtocol(Protocol):
    def lower_logical_circuit(self, logical_circuit: Any, capability: BackendCapabilityModel) -> LoweringResult: ...

class ReferenceSimulatorProtocol(Protocol):
    def execute_reference(self, lowered_result: LoweringResult, shots: int) -> ExecutionJobResult: ...

class ResultVerifierProtocol(Protocol):
    def verify_results(self, reference_job: ExecutionJobResult, observed_job: ExecutionJobResult, alpha_threshold: float = 0.05) -> Dict[str, Any]: ...
```
