# MODULE 7 STAGE 2 — CONSTITUTION

## ARTICLE I — PURPOSE

Module 7 Stage 2 ("Logical-to-Native Lowering & Topology Mapping Domain") establishes the governed lowering layer that transforms certified logical quantum circuits from Module 6 into backend-compatible native circuits constrained by physical qubit topology and gate sets.

---

## ARTICLE II — ABSOLUTE SEMANTIC AUTHORITY & UPSTREAM IMMUTABILITY

1. **Semantic Authority**: Module 4 Stage 4 remains the absolute semantic authority. Lowering success ($\text{LoweringStatus} = \text{LOWERED}$) DOES NOT equal semantic equivalence. Derived native circuits MUST undergo semantic verification before certification.
2. **Upstream Immutability**: Modules 1–5 and Module 6 Stages 1–11 are strictly frozen upstream contracts. Stage 2 SHALL NOT mutate any source code or behavioral state of Modules 1–6 or Stage 1.
3. **Three Gate-Set Isolation**:
   - Evolutionary Gate Vocabulary $GE(k)$ is owned exclusively by Module 6.
   - User Session Baseline $B_u$ is owned exclusively by Module 6.
   - Backend Native Capability $C_{\text{backend}}$ is owned by Module 7 Stage 1.
   - Backend-native operations SHALL NOT be promoted into $GE(k)$ or $B_u$.

---

## ARTICLE III — RESOLUTION OF STAGE 2 CONSTITUTIONAL QUESTIONS (Q1–Q40)

- **Q1: What exactly constitutes a certified logical-circuit input?**
  An immutable `CertifiedLogicalCircuit` artifact from Module 6 Stage 10 carrying valid `logical_circuit_id`, `logical_circuit_hash`, and authentic `semantic_evidence_id` verified by Module 4 Stage 4.
- **Q2: What information must accompany the logical circuit?**
  Logical circuit identity, canonical SHA-256 hash, semantic evidence reference, Module 6 compilation context, Pareto quality records, and audit certification metadata.
- **Q3: What is the exact Stage 1 -> Stage 2 contract?**
  Stage 2 consumes `BackendCapabilityModel` ($C_{\text{backend}}$) via `BackendRegistryProtocol.get_backend()` without bypassing the registry or querying providers directly.
- **Q4: What is the exact Stage 2 -> Stage 3 contract?**
  Stage 2 outputs `LoweringResultArtifact` containing the lowered native gate sequence, physical qubit mapping, lowering provenance, and semantic verification status to Stage 3 Reference Simulator.
- **Q5: What is the exact Stage 2 -> Stage 4 contract?**
  Stage 2 provides provider-neutral native circuit payload and lowering provenance to Stage 4 Cloud Hardware Adapters.
- **Q6: What is the exact Stage 2 -> Stage 5 contract?**
  Stage 2 provides stable `lowering_id` and `native_circuit_hash` references for Stage 5 result retrieval and statistical verification.
- **Q7: Who owns gate decomposition?**
  Module 7 Stage 2 owns logical-to-native gate decomposition rules and transformation pipelines.
- **Q8: Who owns topology mapping?**
  Module 7 Stage 2 owns logical-to-physical qubit mapping (`qubit_mapping: Dict[int, int]`).
- **Q9: Who owns routing?**
  Module 7 Stage 2 owns topology-constrained routing and deterministic SWAP insertion passes.
- **Q10: What constitutes a native gate?**
  An operation belonging to `backend.native_gate_set` or satisfying explicit target device operation contracts.
- **Q11: What does native-gate containment mean?**
  Every operation in the lowered native circuit MUST be contained within `backend.native_gate_set`.
- **Q12: How are logical and physical qubits distinguished?**
  Logical qubits ($q_{\text{logical}}$) represent circuit algorithm registers; physical qubits ($q_{\text{physical}}$) represent hardware device indices on $C_{\text{backend}}$.
- **Q13: How is deterministic qubit mapping guaranteed?**
  By applying deterministic initial mapping policies and deterministic tie-breaking without random seeds or un-ordered dict iterations.
- **Q14: How are topology violations detected?**
  By validating multi-qubit interaction pairs against `backend.topology_coupling_map`.
- **Q15: When is routing permitted?**
  When multi-qubit interaction edges in the native circuit do not directly exist in `backend.topology_coupling_map`.
- **Q16: Can routing insert SWAP operations?**
  Yes, provided SWAP insertions are explicit, deterministic, provenance-tracked, and semantically verified.
- **Q17: How are inserted operations represented in provenance?**
  Via explicit lowering diagnostics (`inserted_swap_count`, `routing_overhead`, `gate_expansion_ratio`) recorded in `lowering_provenance`.
- **Q18: How are gate parameters transformed?**
  Via deterministic analytical mappings (e.g. angle normalization, parameter scaling) preserving mathematical equivalence.
- **Q19: What happens when a parameter is unsupported?**
  Returns structured failure `ExecutionFailureCategory.LOWERING_FAILURE` or `UNSUPPORTED_PARAMETER`.
- **Q20: Are ancilla qubits permitted?**
  Only if explicitly allowed by `LoweringPolicy` and satisfying backend qubit capacity limits (`qubit_count`).
- **Q21: Who owns ancilla allocation?**
  Module 7 Stage 2 owns ancilla allocation and initialization/restoration tracking.
- **Q22: What constitutes lowering success?**
  Lowering produced a valid native circuit satisfying $C_{\text{backend}}$ gate set & topology AND semantic verification confirmed equivalence (`VERIFIED`).
- **Q23: What constitutes lowering failure?**
  Decomposition or routing failed to produce a backend-compatible circuit (`LOWERING_FAILURE`).
- **Q24: What constitutes semantic non-equivalence?**
  Lowering generated a candidate native circuit but semantic verification failed (`SEMANTICALLY_NON_EQUIVALENT`).
- **Q25: What constitutes inconclusive semantic verification?**
  Semantic verification could not definitively prove or disprove equivalence (`INCONCLUSIVE`).
- **Q26: Can Stage 2 automatically retry with another strategy?**
  No automatic retries without explicit user/governance authorization.
- **Q27: Can Stage 2 automatically choose another backend?**
  No automatic backend substitution is permitted.
- **Q28: Can Stage 2 automatically recompile through Module 6?**
  No automatic recompilation through Module 6 is permitted.
- **Q29: Can Stage 2 modify GE(k)?**
  NO. $GE(k)$ is 100% frozen in Module 6.
- **Q30: Can Stage 2 modify user baseline?**
  NO. $B_u$ is 100% frozen in Module 6.
- **Q31: Can Stage 2 modify the logical circuit?**
  NO. Input logical circuit is immutable; native circuit is a derived artifact.
- **Q32: What is the semantic verification interface?**
  `SemanticVerifierProtocol` delegating verification to Module 4 Stage 4 semantic authority.
- **Q33: How is semantic verification provenance linked?**
  Via `semantic_verification_reference` and SHA-256 digest in `LoweringResultArtifact`.
- **Q34: How is lowering identity generated?**
  Deterministic SHA-256 digest computed over `logical_circuit_id`, `backend_id`, `policy_hash`, and `native_gate_sequence`.
- **Q35: How is native circuit identity generated?**
  Deterministic SHA-256 digest computed over canonical serialization of native gate sequence and physical qubit mapping.
- **Q36: How is deterministic serialization guaranteed?**
  Canonical JSON serialization sorted by keys (`sort_keys=True`) with UTF-8 encoding.
- **Q37: How is capability version linked to lowering?**
  `capability_version` and `capability_hash` are explicitly stored in `LoweringResultArtifact`.
- **Q38: How is Stage 11 lineage extended?**
  Lowering events append immutable lineage records to Stage 11 repository.
- **Q39: Which execution metrics belong to Stage 2?**
  `native_gate_count`, `circuit_depth`, `gate_expansion_ratio`, `inserted_swap_count`, `routing_overhead`.
- **Q40: What is the exact Stage 2 completion criterion?**
  Formal initialization approval, complete governance documentation, directory scaffold, 100% test pass rate, and zero upstream regressions.

---

## ARTICLE IV — HARDWARE, CLOUD, AND NOISE BOUNDARIES

- **HARDWARE EXECUTION**: 0% during Stage 2 Initialization.
- **CLOUD EXECUTION**: 0% during Stage 2 Initialization.
- **NOISE SIMULATION**: 0% during Stage 2 Initialization.
