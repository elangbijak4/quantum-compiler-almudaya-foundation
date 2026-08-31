# MODULE 7 STAGE 3 — SCOPE DEFINITION

## 1. In-Scope Responsibilities

1. **Local Reference Simulator Runtime**: Provider-neutral statevector and shot-sampled quantum execution runtime operating locally under the Local First Policy.
2. **Pre-Execution Validation**: Verifying that input circuits carry `LoweringStatus.SEMANTICALLY_VERIFIED` and valid $C_{\text{backend}}$ native gate containment before execution.
3. **Deterministic State Evolution**: Applying unitary matrix operators to ideal statevector $\vert\psi\rangle = \sum c_k \vert k\rangle$.
4. **Computational Basis Measurement & Shot Sampling**: Projecting statevector amplitudes into computational basis bitstring probability distributions and simulated shot counts.
5. **Execution Result Model (`SimulatorJobResult`)**: Generating immutable result artifacts with full 64-character SHA-256 canonical hashing and complete execution lineage provenance.

---

## 2. Explicit Out-of-Scope (Non-Scope)

1. **Cloud & Provider SDK Execution**: Zero cloud API calls, authentication tokens, or provider SDKs (`CLOUD EXECUTION: 0%`).
2. **Physical Hardware Execution**: Zero hardware device contact (`HARDWARE EXECUTION: 0%`).
3. **Hardware Noise Modeling**: Zero stochastic hardware error models (`NOISE SIMULATION: 0%`).
4. **Circuit Modification / Relowering**: Stage 3 DOES NOT modify input circuits or invoke lowering passes.
5. **Statistical Verification**: Result verification and chi-squared testing belong to Stage 5.
