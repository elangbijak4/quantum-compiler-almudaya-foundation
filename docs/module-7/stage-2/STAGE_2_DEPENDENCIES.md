# MODULE 7 STAGE 2 — DEPENDENCIES & CONSUMPTION MATRIX

## 1. Upstream Consumed Contracts

- **Module 6 Stage 10**: Reads `CertifiedLogicalCircuit` as immutable input.
- **Module 7 Stage 1**: Consumes `BackendCapabilityModel` ($C_{\text{backend}}$) via `BackendRegistryProtocol`.
- **Module 4 Stage 4**: Consumes semantic equivalence verification authority via `SemanticVerificationAdapterProtocol`.

---

## 2. Downstream Provided Contracts

- **Module 7 Stage 3 (Reference Simulator)**: Provides `LoweringResultArtifact` and `NativeCircuitArtifact` for local virtual simulation execution.
- **Module 7 Stage 4 (Cloud Adapters)**: Provides provider-neutral `NativeCircuitArtifact` payload for submission to physical hardware providers.
- **Module 7 Stage 5 (Result Verification)**: Provides `lowering_id` and `native_circuit_hash` for statistical measurement result verification.
- **Module 6 Stage 11 (Lineage)**: Appends lowering execution records to Stage 11 historical lineage repository.
