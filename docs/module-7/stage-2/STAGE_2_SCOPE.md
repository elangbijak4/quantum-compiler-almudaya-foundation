# MODULE 7 STAGE 2 — SCOPE DEFINITION

## 1. In-Scope Responsibilities

1. **Lowering Policy & Configuration (`LoweringPolicy`)**: Defining explicit policies for decomposition, qubit mapping, routing strategies, ancilla constraints, and tie-breaking.
2. **Logical-to-Native Decomposition Contract**: Defining mathematical decomposition rules from logical gates to backend native operations.
3. **Logical-to-Physical Qubit Mapping (`qubit_mapping: Dict[int, int]`)**: Assigning logical register indices to physical device qubit indices.
4. **Topology-Constrained Routing**: SWAP insertion and coupling graph constraint enforcement.
5. **Lowering Result Artifact (`LoweringResultArtifact`)**: Immutable output model tying together logical circuit ID, backend capability hash, native circuit artifact, mapping, and semantic verification status.
6. **Semantic Verification Integration**: Protocol contract for delegating semantic verification of native candidate circuits to Module 4 Stage 4 authority.

---

## 2. Explicit Out-of-Scope (Non-Scope)

1. **Production Decomposition/Routing Engines**: Production engine logic deferred to Stage 2 Engine Implementation.
2. **Virtual Execution**: Production reference simulation belongs to Stage 3.
3. **Cloud Provider Adapters**: Provider adapters belong to Stage 4.
4. **Hardware Execution**: Hardware execution = 0%.
5. **Measurement Verification**: Result verification belongs to Stage 5.
6. **Module 6 State Mutation**: Zero mutation to $GE(k)$, $B_u$, logical circuits, or Stage 11 lineage.
