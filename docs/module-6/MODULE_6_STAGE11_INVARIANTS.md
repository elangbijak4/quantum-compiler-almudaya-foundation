# MODULE 6 STAGE 11 INVARIANTS

## Non-Negotiable Invariants

1. **Modules 1–5 Immutability**: `src/module1/` .. `src/module5/` are strictly frozen (0 edits permitted).
2. **Stages 1–10 Immutability**: Stage 1–10 implementations and governance contracts remain frozen.
3. **Semantic Authority Invariant**: Stage 4 Level 6 Semantic Equivalence remains the absolute correctness authority.
4. **Vocabulary Containment Invariant**: All operations must enforce $g \in G_{\text{effective}}$. Zero hidden gate expansion.
5. **No Automatic Gate Promotion**: No automatic modification of $GE(k)$.
6. **No Session Baseline Mutation**: No alteration of user session baseline $B_u$.
7. **No Circuit Mutation**: Stage 11 does not alter, optimize, or rewrite circuits.
8. **No Hardware Execution**: Hardware execution = `0%`.
9. **No Physical Noise Simulation**: Noise simulation = `0%`.
10. **Deterministic Trace Reproducibility**: Identical inputs yield byte-identical lineage trace reports.
