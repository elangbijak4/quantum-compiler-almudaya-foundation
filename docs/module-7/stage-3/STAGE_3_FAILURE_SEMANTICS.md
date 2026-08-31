# MODULE 7 STAGE 3 — FAILURE SEMANTICS & TAXONOMY

## 1. Stage 3 Failure Classifications

1. `EXECUTION_INPUT_INVALID`: Missing or malformed lowered native circuit artifact or unverified lowering status.
2. `BACKEND_CAPABILITY_MISMATCH`: Circuit qubit references or native operations exceed backend capability bounds.
3. `UNSUPPORTED_NATIVE_GATE`: Native operation is not executable by the reference simulator.
4. `EXECUTION_RESOURCE_EXHAUSTED`: Qubit count or statevector memory exceeds maximum simulator capacity limit ($N_{\text{qubits}} > 32$).
5. `STATE_EVOLUTION_FAILURE`: Numerical overflow or invalid operator matrix evaluation during state vector evolution.
6. `MEASUREMENT_FAILURE`: Computational basis measurement projection failure.
7. `EXECUTION_FAILURE`: General simulator execution engine failure.
8. `EXECUTION_INCONCLUSIVE`: Execution produced indeterminate statevector bounds or undersampled shot statistics.

---

## 2. Recovery Policy

- Failures produce structured `SimulatorJobResult` with `status = FAILED` or `REJECTED`.
- Failures SHALL NOT alter upstream state or trigger automatic recompilation.
