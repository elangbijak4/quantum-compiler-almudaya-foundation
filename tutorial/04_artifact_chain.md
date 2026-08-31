# 04. Artifact Chain & Identity

Understand how artifacts are identified, tracked, and linked across the compiler pipeline.

---

## Artifact Record Fields

Every computational artifact produced by the compiler contains:
- `artifact_id`: Unique string identifier (e.g. `LOG_CIRC_01`).
- `artifact_type`: Formal category (e.g. `SourceCode`, `AMLArtifact`, `UTMArtifact`, `SemanticCertificate`, `LogicalCircuit`, `NativeCircuit`, `SimulationResult`, `VerificationRecord`).
- `parent_artifact_id`: ID of the parent artifact from which this artifact was derived.
- `hash`: SHA-256 cryptographic digest of artifact content.
- `status`: Execution status (`SUCCESS`, `FAILED`, `VERIFIED`).
- `provenance`: Dict containing transformation history and parameters.

---

## Parent/Child Linkage Invariant

Across every consecutive stage transition:

```text
child.parent_artifact_id == parent.artifact_id
```

### Example Artifact Chain:
1. `SRC_01` (parent: `None`)
2. `AML_01` (parent: `SRC_01`)
3. `UTM_01` (parent: `AML_01`)
4. `CERT_01` (parent: `UTM_01`)
5. `LOG_CIRC_01` (parent: `CERT_01`)
6. `NAT_CIRC_01` (parent: `LOG_CIRC_01`)
7. `SIM_RES_01` (parent: `NAT_CIRC_01`)
8. `VER_REC_01` (parent: `SIM_RES_01`)

---

## Artifact Type Safety

The CLI enforces strict type safety. Attempting an invalid transition (e.g., executing lowering on a `SimulationResult`) will be explicitly rejected:

```bash
python -m src.application.cli.main execute SIM_RES_01 --backend UNSUPPORTED_BACKEND
```
*Result: Exit Code `3 (EXECUTION_FAILURE)` with `BACKEND_UNSUPPORTED` error classification.*
