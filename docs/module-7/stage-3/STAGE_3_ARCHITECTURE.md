# MODULE 7 STAGE 3 — ARCHITECTURE

```
+-----------------------------------------------------------------------------------+
|                            INPUT ARTIFACTS                                        |
|  [Verified LoweringResultArtifact] (M7 Stage 2) + [BackendCapabilityModel] (M7 S1)|
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|             MODULE 7 STAGE 3: LOCAL REFERENCE SIMULATOR RUNTIME                   |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   | 1. Pre-Execution Gate & Verification Validation                           |   |
|   |    - Assert status == SEMANTICALLY_VERIFIED                              |   |
|   |    - Assert all operations in native_gate_set                             |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | 2. Statevector Evolution Engine (|0...0> -> U_1 ... U_n -> |psi_final>)    |   |
|   |    - Deterministic complex128 statevector evolution                       |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | 3. Computational Basis Measurement & PRNG Shot Sampling                   |   |
|   |    - Exact probability amplitudes: P(k) = |c_k|^2                             |   |
|   |    - Seeded PRNG bitstring shot sampling                                      |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    OUTPUT: SimulatorJobResult                                     |
| (Status: COMPLETED / REJECTED / FAILED / INCONCLUSIVE)                            |
+-----------------------------------------------------------------------------------+
```

---

## Key Architectural Invariants

1. **Local First Policy**: Execution occurs entirely within local process memory.
2. **Determinism**: Statevector evolution is 100% deterministic; shot sampling uses explicit PRNG seed.
3. **Derived Output**: Input native circuit is immutable; `SimulatorJobResult` is a derived execution artifact.
