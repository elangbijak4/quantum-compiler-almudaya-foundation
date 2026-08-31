# MODULE 7 STAGE 5 — INVARIANTS & CONSTRAINTS

1. **Immutability Invariant**: Input execution results, reference probability distributions, and verification policies are 100% immutable throughout evaluation.
2. **Determinism Invariant**: Statistical distance calculation for identical inputs and policy version MUST return identical float metric values and verification decision.
3. **No Automatic Re-execution Invariant**: Stage 5 MUST NOT automatically trigger re-lowering, re-execution, or shot count modification.
4. **Append-Only Lineage Invariant**: Stage 5 appends new verification records to Stage 11 without modifying or deleting past historical lineage records.
5. **Credential Isolation Invariant**: Zero raw API keys, tokens, or passwords enter verification artifacts, hashes, logs, or lineage records.
