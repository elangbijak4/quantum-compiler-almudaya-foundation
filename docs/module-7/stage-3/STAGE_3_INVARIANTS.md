# MODULE 7 STAGE 3 — INVARIANTS

1. **Local First Policy**: Stage 3 operates 100% locally. Zero network calls, cloud API invocations, or hardware authentication.
2. **Upstream Freeze**: Modules 1–5, Module 6 Stages 1–11, and Module 7 Stages 1–2 are 100% frozen.
3. **Execution Eligibility**: Only native circuits with `LoweringStatus.SEMANTICALLY_VERIFIED` are eligible for execution. Unverified circuits are rejected (`SimulationExecutionStatus.REJECTED`).
4. **Three Gate-Set Isolation**: Simulator operations SHALL NOT mutate Module 6 $GE(k)$ or $B_u$.
5. **Exact vs Sampled Distinction**: `STATEVECTOR_EXACT` probability amplitudes $\vert c_k\vert^2$ are explicitly distinguished from `SAMPLED_SHOTS` measurement count histograms.
6. **Hardware & Cloud Boundaries**: `CLOUD EXECUTION: 0%`, `HARDWARE EXECUTION: 0%`, `NOISE SIMULATION: 0%`.
