# MODULE 7 STAGE 2 — FAILURE SEMANTICS & TAXONOMY

## 1. Stage 2 Failure Classifications

1. `LOWERING_INPUT_INVALID`: Missing or malformed certified logical circuit input or missing semantic evidence.
2. `BACKEND_CAPABILITY_MISMATCH`: Logical circuit exceeds backend qubit limit, max shots, or native gate set requirements.
3. `UNSUPPORTED_OPERATION`: Logical gate cannot be decomposed into declared native gate set.
4. `UNSUPPORTED_PARAMETER`: Gate parameter cannot be transformed to backend domain constraints.
5. `DECOMPOSITION_FAILURE`: Gate decomposition rule evaluation failed.
6. `TOPOLOGY_FAILURE`: Routing pass failed to satisfy physical device coupling graph.
7. `QUBIT_MAPPING_FAILURE`: Logical-to-physical qubit allocation failed.
8. `ROUTING_FAILURE`: SWAP insertion pass failed or exceeded max depth limit.
9. `ANCILLA_FAILURE`: Ancilla allocation violated policy limits.
10. `NATIVE_CIRCUIT_INVALID`: Lowered native circuit payload failed validation checks.
11. `SEMANTIC_NON_EQUIVALENCE`: Candidate native circuit failed semantic equivalence verification against original logical circuit.
12. `SEMANTIC_VERIFICATION_INCONCLUSIVE`: Semantic verification could not definitively confirm equivalence.

---

## 2. Policy Invariants

- Failures MUST produce structured `LoweringResultArtifact` with `status = FAILED` or `SEMANTICALLY_NON_EQUIVALENT`.
- Failures SHALL NOT alter upstream state or retry automatically without explicit user authorization.
