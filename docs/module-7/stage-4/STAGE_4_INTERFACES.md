# MODULE 7 STAGE 4 — INTERFACE SPECIFICATION

## 1. Data Contract Definitions

```python
@dataclass(frozen=True)
class CloudExecutionRequest:
    request_id: str
    native_circuit_id: str
    native_circuit_hash: str
    backend_id: str
    provider_id: str
    capability_hash: str
    lowering_id: str
    shots: int = 1000
    credential_ref: Optional[str] = None
    request_hash: str = ""


@dataclass(frozen=True)
class CloudJobHandle:
    job_id: str
    provider_job_id: str
    request_id: str
    provider_id: str
    backend_id: str
    status: CloudExecutionLifecycleStatus
    handle_hash: str = ""


@dataclass(frozen=True)
class ProviderNeutralExecutionResult:
    job_id: str
    provider_job_id: str
    native_circuit_hash: str
    backend_id: str
    provider_id: str
    environment_type: ExecutionEnvironmentType
    status: CloudExecutionLifecycleStatus
    shots: int
    measurement_counts: Dict[str, int]
    measurement_distribution: Dict[str, float]
    provenance: Dict[str, Any] = field(default_factory=dict)
    result_hash: str = ""
```

---

## 2. Cloud Backend Adapter Protocol

```python
class CloudBackendAdapterProtocol(Protocol):
    def validate_capability(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
    ) -> bool:
        ...

    def submit_job(
        self,
        request: CloudExecutionRequest,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
    ) -> CloudJobHandle:
        ...

    def get_job_status(self, handle: CloudJobHandle) -> CloudJobHandle:
        ...

    def retrieve_result(self, handle: CloudJobHandle) -> ProviderNeutralExecutionResult:
        ...

    def cancel_job(self, handle: CloudJobHandle) -> CloudJobHandle:
        ...
```
