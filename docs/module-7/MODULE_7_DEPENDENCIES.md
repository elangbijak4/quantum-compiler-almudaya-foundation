# MODULE 7 — DEPENDENCIES & ARTIFACT CONSUMPTION MATRIX

## 1. Upstream Consumed Contracts

- **Module 6 Stage 10**: Consumes `GovernanceAuditReport` and `AuditCertificate` as certified logical circuit inputs.
- **Module 6 Stage 11**: Consumes `HistoricalLineageRepository` via append-only `append_event()` / `append_record()` interfaces for persistent execution lineage logging.
- **Module 4**: Consumes Level 6 semantic verification rules to validate that transpilation lowering preserves logical semantics.

---

## 2. Downstream Isolation

- Modules 1–6 DO NOT depend on Module 7.
- Core compiler runs completely standalone without Module 7.
- External provider SDKs (Qiskit, Braket, Cirq) exist strictly inside Module 7 Stage 4 adapters.
