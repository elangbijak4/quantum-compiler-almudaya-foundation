# MODULE 6 STAGE 10 — INTERFACE SPECIFICATIONS

## 1. Interface Definitions

### 1.1 `GovernanceAuditor.audit_compilation`
```python
@classmethod
def audit_compilation(
    cls,
    algorithm_id: str,
    quality_report: Optional[QualityAnalysisReport] = None,
    context: Optional[EffectiveCompilationContext] = None,
) -> GovernanceAuditReport: ...
```
- **Inputs**: `algorithm_id`, optional `QualityAnalysisReport`, optional `EffectiveCompilationContext`.
- **Outputs**: `GovernanceAuditReport`.
- **Preconditions**: Stages 1–9 outputs must be immutable read-only objects.
- **Postconditions**: Produces deterministic `AuditCertificate` and report hash. Zero circuit mutation.

### 1.2 `serialize_audit_certificate` / `deserialize_audit_certificate`
```python
def serialize_audit_certificate(cert: AuditCertificate) -> str: ...
def deserialize_audit_certificate(json_str: str) -> AuditCertificate: ...
```
- **Guarantees**: Canonical JSON formatting (`sort_keys=True`), round-trip equality `deserialize(serialize(X)) == X`.
