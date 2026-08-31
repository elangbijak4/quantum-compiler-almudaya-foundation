# MODULE 7 STAGE 2 — STATE OWNERSHIP & BOUNDARY DOMAINS

## 1. Domain State Ownership

- **Stage 2 State Ownership**: Owns Lowering Policies (`LoweringPolicy`), logical-to-native decomposition rules, logical-to-physical qubit mappings (`qubit_mapping`), topology routing passes, derived native circuit artifacts (`NativeCircuitArtifact`), and lowering result artifacts (`LoweringResultArtifact`).
- **Module 6 State Ownership**: Owns Evolutionary Gate Vocabulary $GE(k)$, User Session Baseline $B_u$, effective compilation context, Pareto quality states, audit certification, and historical lineage.
- **Stage 1 State Ownership**: Owns Backend Capability Models ($C_{\text{backend}}$) and Backend Registry.

---

## 2. Boundary Invariants

- Stage 2 SHALL NOT mutate any Module 6 or Stage 1 state objects.
- Stage 2 SHALL NOT modify $GE(k)$ or $B_u$.
- Stage 2 output is a derived execution-domain artifact.
