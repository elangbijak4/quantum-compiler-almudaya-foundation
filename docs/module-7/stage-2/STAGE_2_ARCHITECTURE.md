# MODULE 7 STAGE 2 — ARCHITECTURE

```
+-----------------------------------------------------------------------------------+
|                            INPUT ARTIFACTS                                        |
|  [Certified Logical Circuit] (M6 Stage 10) + [Backend Capability Model C_backend]  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    MODULE 7 STAGE 2: LOWERING DOMAIN                              |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   | 1. Lowering Policy & Gate Decomposition                                   |   |
|   |    - Map logical operations to native_gate_set                            |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | 2. Logical-to-Physical Qubit Mapping & Topology Routing                   |   |
|   |    - Map q_logical -> q_physical                                          |   |
|   |    - Enforce topology_coupling_map & insert SWAPs if required             |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | 3. Candidate Native Circuit Generation & Semantic Verification            |   |
|   |    - Generate NativeCircuitArtifact                                       |   |
|   |    - Delegate verification to Module 4 Stage 4 authority                 |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    OUTPUT: LoweringResultArtifact                                 |
| (Status: VERIFIED / LOWERED / SEMANTICALLY_NON_EQUIVALENT / FAILED)               |
+-----------------------------------------------------------------------------------+
```

---

## Architectural Principles

1. **Semantic Verification Pre-requisite**: Lowering success is NOT equivalence. Every lowered native candidate MUST undergo semantic verification.
2. **Deterministic Routing**: SWAP insertion and mapping heuristics MUST be deterministic without random choices or un-ordered dict iterations.
3. **Derived Artifact Isolation**: The original certified logical circuit remains 100% immutable; native circuits are derived output artifacts.
