# MODULE 7 — CONSTITUTIONAL INVARIANTS

1. **Upstream Immutability**: Modules 1–6 source code and state implementations are 100% frozen.
2. **Semantic Equivalence Preservation**: Module 4 Level 6 semantic equivalence is the sole semantic authority. Lowering MUST NOT alter logical circuit semantics.
3. **Three Gate-Set Isolation**: Evolutionary Gate Vocabulary $GE(k)$, User Session Baseline $B_u$, and Backend Native Capability $C_{\text{backend}}$ MUST remain strictly distinct.
4. **Credential Privacy**: Raw secrets MUST NEVER enter circuit identity, hash computations, or serialized Stage 11 lineage records.
5. **Local First Execution**: Stage 3 local reference simulator MUST be fully verified prior to cloud hardware execution.
6. **Hardware & Cloud Boundaries**: Hardware execution = 0%, Cloud execution = 0%, Noise simulation = 0% during Initialization.
7. **Append-Only Execution Lineage**: Execution events appended to Stage 11 MUST NEVER modify or overwrite prior historical audit records.
