# MODULE 7 STAGE 1 — INTERFACE SPECIFICATION

## 1. Data Contract Definitions

```python
@dataclass(frozen=True)
class BackendCapabilityModel:
    backend_id: str
    provider_id: str
    backend_type: str  # "VIRTUAL_SIMULATOR" or "PHYSICAL_HARDWARE"
    qubit_count: int
    native_gate_set: Tuple[str, ...]
    topology_coupling_map: Tuple[Tuple[int, int], ...]
    max_shots: int
    supports_custom_pulses: bool = False
    capability_version: str = "1.0.0"
    capability_hash: str = ""
```

---

## 2. Registry Protocol Definition

```python
class BackendRegistryProtocol(Protocol):
    def register_backend(self, capability: BackendCapabilityModel) -> None:
        ...

    def get_backend(self, backend_id: str) -> Optional[BackendCapabilityModel]:
        ...

    def list_backends(self) -> Tuple[BackendCapabilityModel, ...]:
        ...
```
