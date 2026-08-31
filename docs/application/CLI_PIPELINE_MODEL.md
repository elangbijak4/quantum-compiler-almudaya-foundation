# APPLICATION / PRODUCT LAYER — CLI PIPELINE MODEL

## Pipeline Mode Semantics

Pipeline mode (`compile <input>`) is a convenience command that orchestrates the multi-module compilation pipeline while preserving full stage transparency.

```text
Classical Input -> AML -> UTM -> RUTM -> Semantic Cert -> Quantum Map -> Optimize -> Lower -> Simulate/Execute -> Verify -> Lineage
```

### Invariants:
1. Pipeline mode MUST NOT obscure intermediate stage artifacts.
2. Pipeline mode output exposes full artifact IDs and SHA-256 hashes for every stage.
3. Pipeline mode does NOT bypass stage boundaries or authority rules.
