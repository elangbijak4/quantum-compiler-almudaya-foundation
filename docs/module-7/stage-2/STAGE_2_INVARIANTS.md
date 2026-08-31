# MODULE 7 STAGE 2 — INVARIANTS

1. **Upstream Freeze**: Modules 1–5, Module 6 Stages 1–11, and Module 7 Stage 1 are 100% frozen. Zero source code modifications permitted.
2. **Lowering Success $\neq$ Semantic Equivalence**: A candidate native circuit MUST be semantically verified before status is set to `VERIFIED`.
3. **Three Gate-Set Isolation**:
   - $GE(k)$: Module 6 Evolutionary Gate Vocabulary.
   - $B_u$: Module 6 User Session Baseline.
   - $C_{\text{backend}}$: Module 7 Stage 1 Backend Native Capability.
   - Backend native gates SHALL NOT be added to $GE(k)$ or $B_u$.
4. **Input Immutability**: Certified logical circuits are strictly read-only inputs. Native circuits are derived output artifacts.
5. **No Automatic Fallback or Recompilation**: Stage 2 SHALL NOT automatically select another backend or trigger Module 6 recompilation upon failure.
6. **No Execution Authorization**: Stage 2 SHALL NOT execute circuits on virtual simulators or hardware (`HARDWARE EXECUTION: 0%`, `CLOUD EXECUTION: 0%`, `NOISE SIMULATION: 0%`).
