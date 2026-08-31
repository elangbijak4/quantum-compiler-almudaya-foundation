# MODULE 7 STAGE 3 — DEPENDENCIES & CONSUMPTION MATRIX

## 1. Upstream Consumed Contracts

- **Module 7 Stage 2**: Consumes verified `LoweringResultArtifact` and derived `NativeCircuitArtifact`.
- **Module 7 Stage 1**: Consumes `BackendCapabilityModel` ($C_{\text{backend}}$) native gate set and qubit capacity.
- **Module 4 Stage 4**: Verifies semantic evidence reference presence prior to execution.

---

## 2. Downstream Provided Contracts

- **Module 7 Stage 4 (Cloud Adapters)**: Provides standard `ReferenceSimulatorProtocol` execution interface for cloud hardware adapters to implement for external providers.
- **Module 7 Stage 5 (Result Verification)**: Provides `SimulatorJobResult` measurement counts and distributions for statistical chi-squared verification.
- **Module 6 Stage 11 (Lineage)**: Appends simulator execution records to Stage 11 historical lineage repository.
