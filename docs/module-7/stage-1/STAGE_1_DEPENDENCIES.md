# MODULE 7 STAGE 1 — DEPENDENCIES & CONSUMPTION MATRIX

## 1. Upstream Consumed Contracts

- **Module 6 Stage 10**: Reads certified logical circuit parameters to perform preliminary capability compatibility checks.
- **Module 6 Stage 11**: Provides stable `capability_hash` references to be recorded in Stage 11 execution lineage events.

---

## 2. Downstream Provided Contracts

- **Module 7 Stage 2 (Lowering)**: Provides `BackendCapabilityModel` ($C_{\text{backend}}$) native gate set and topology coupling map for transpilation decomposition and routing.
- **Module 7 Stage 3 (Reference Simulator)**: Provides registered `VIRTUAL_SIMULATOR` capability descriptors.
- **Module 7 Stage 4 (Cloud Adapters)**: Provides standard provider-neutral registry interface (`BackendRegistryProtocol`).
