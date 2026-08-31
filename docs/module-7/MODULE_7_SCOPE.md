# MODULE 7 — SCOPE DEFINITION

## 1. In-Scope Responsibilities

1. **Backend Capability Registry ($C_{\text{backend}}$)**: Provider-neutral representation of native gate sets, qubit counts, topology graphs, max shots, and execution models.
2. **Logical-to-Native Lowering Engine**: Transpilation pass decomposing logical gates into native backend gates and mapping logical qubits to physical device connectivity graphs.
3. **Local Virtual Reference Simulator Runtime**: Provider-neutral reference simulator for local, deterministic execution verification (Local First Policy).
4. **Cloud Hardware Provider Adapters**: Modular adapters for cloud platforms (IBM, AWS, Google, Microsoft).
5. **Shot Measurement Retrieval & Result Model**: Provider-neutral measurement count/distribution models (`ExecutionJobResult`).
6. **Statistical Result Verification**: Distribution comparison metrics (Hellinger / Kolmogorov-Smirnov distance) evaluating execution results against reference expectations.
7. **Stage 11 Lineage Extension**: Append-only persistent execution event logging in `HistoricalLineageRepository`.

---

## 2. Explicit Out-of-Scope (Non-Scope)

1. **Semantic Equivalence Definition**: Module 4 / Module 6 Stage 4 Level 6 remains the sole semantic authority.
2. **Evolutionary Gate Promotion**: Module 6 Stage 5/6 owns evolutionary gate vocabulary $GE(k)$.
3. **User Baseline Modification**: Module 6 Stage 6 owns user session baseline $B_u$.
4. **Compiler Audit Certification**: Module 6 Stage 10 owns certification.
5. **Historical Lineage Modification**: Existing Stage 11 historical records are immutable and append-only.
6. **Production Hardware/Cloud Execution During Initialization**: Hardware execution = 0%, Cloud execution = 0%.
