# MODULE 7 STAGE 1 — INVARIANTS

1. **Upstream Freeze**: Modules 1–5 and Module 6 Stages 1–11 are 100% frozen. Zero code edits permitted.
2. **Three Gate-Set Isolation**:
   - $GE(k)$: Module 6 Evolutionary Gate Vocabulary.
   - $B_u$: Module 6 User Session Baseline.
   - $C_{\text{backend}}$: Module 7 Stage 1 Backend Native Capability.
   - These three gate sets MUST NEVER be collapsed into a single object or state.
3. **No Credential Exposure**: Raw credentials MUST NEVER be present in capability descriptors or canonical hashes.
4. **Deterministic Identity**: `capability_hash` MUST be a full 64-character hex digest computed deterministically from canonical JSON.
5. **No Execution Authorization**: Stage 1 SHALL NOT execute circuits on hardware or cloud APIs (`HARDWARE EXECUTION: 0%`, `CLOUD EXECUTION: 0%`).
