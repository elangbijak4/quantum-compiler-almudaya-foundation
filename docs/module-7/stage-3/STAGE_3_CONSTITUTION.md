# MODULE 7 STAGE 3 — CONSTITUTION

## ARTICLE I — PURPOSE & LOCAL FIRST POLICY

Module 7 Stage 3 ("Local Virtual Reference Quantum Simulator Runtime") establishes the governed local execution domain. Under the **Local First Policy**, Stage 3 provides an ideal, deterministic virtual quantum computer runtime capable of executing semantically verified native circuits produced by Stage 2.

---

## ARTICLE II — ABSOLUTE EXECUTION BOUNDARIES & AUTHORITY

1. **Local Only Policy**: Stage 3 operates 100% locally. No cloud provider APIs, third-party SDKs, hardware credentials, or physical quantum devices are accessed.
   - `CLOUD EXECUTION: 0%`
   - `HARDWARE EXECUTION: 0%`
   - `NOISE SIMULATION: 0%` (Ideal reference machine).
2. **Upstream Immutability**: Modules 1–5, Module 6 Stages 1–11, and Module 7 Stages 1–2 are strictly frozen upstream contracts. Stage 3 SHALL NOT mutate any source code or behavioral state of upstream modules.
3. **Execution Eligibility**: Stage 3 accepts ONLY native circuits carrying `LoweringStatus.SEMANTICALLY_VERIFIED` and valid `semantic_verification_reference`. Unverified, non-equivalent, or failed circuits MUST NOT be executed.
4. **Three Gate-Set Isolation**:
   - Evolutionary Gate Vocabulary $GE(k)$ is owned exclusively by Module 6.
   - User Session Baseline $B_u$ is owned exclusively by Module 6.
   - Backend Native Capability $C_{\text{backend}}$ is owned by Module 7 Stage 1.
   - Simulator operations SHALL NOT mutate $GE(k)$ or $B_u$.

---

## ARTICLE III — RESOLUTION OF STAGE 3 CONSTITUTIONAL QUESTIONS (Q1–Q30)

- **Q1: What constitutes executable input?**
  A Stage 2 `LoweringResultArtifact` containing a `NativeCircuitArtifact` with status `SEMANTICALLY_VERIFIED` and valid `semantic_verification_reference`.
- **Q2: Who owns execution authority?**
  Module 7 Stage 3 owns local reference quantum execution. It does NOT own compilation, lowering, optimization, or semantic equivalence certification.
- **Q3: What is the reference simulator's semantic role?**
  To execute verified native circuits in a local, deterministic reference environment confirming quantum computational behavior under the Local First Policy.
- **Q4: What constitutes valid native input?**
  A `NativeCircuitArtifact` whose operations belong entirely to `backend_capability.native_gate_set` and whose physical qubit references conform to `qubit_count` and `topology_coupling_map`.
- **Q5: What is the state representation?**
  Statevector representation $\vert\psi\rangle = \sum c_k \vert k\rangle$ initialized to $\vert 0\dots 0\rangle$.
- **Q6: What is measurement semantics?**
  Computational basis Z-measurement projecting statevector amplitudes into computational basis bitstrings.
- **Q7: What is shot semantics?**
  Sampled measurement occurrences across $N_{\text{shots}}$ repeated simulated experiments.
- **Q8: What is exact versus sampled output?**
  Exact output = statevector probability amplitudes ($P(k) = \vert c_k\vert^2$); Sampled output = discrete measurement bitstring frequency counts ($\text{counts}[k]$).
- **Q9: What is deterministic execution?**
  Exact statevector state evolution is 100% deterministic; sampled shot distributions are deterministically reproducible via seeded PRNG.
- **Q10: What resource limits apply?**
  Maximum qubits $N_{\text{qubits}} \le 32$, max statevector memory $\approx 64\text{ GB}$, max shots $\le 1,000,000$, max depth $\le 10,000$.
- **Q11: What happens on resource exhaustion?**
  Pre-execution check rejects request with explicit failure `EXECUTION_RESOURCE_EXHAUSTED`. No silent truncation or approximation.
- **Q12: Can Stage 3 mutate circuits?**
  NO. Input native circuits are strictly read-only.
- **Q13: Can Stage 3 relower circuits?**
  NO. Relowering is owned by Stage 2.
- **Q14: Can Stage 3 select another backend?**
  NO. Automatic backend substitution is prohibited.
- **Q15: Can Stage 3 modify GE(k)?**
  NO. $GE(k)$ is 100% frozen in Module 6.
- **Q16: How is Module 4 semantic authority preserved?**
  Stage 3 verifies `semantic_verification_status == "VERIFIED"` before execution and exposes execution evidence for optional downstream cross-checking against Module 4 expectations.
- **Q17: How is execution evidence represented?**
  Via `SimulatorJobResult` containing `execution_id`, `job_hash`, `measurement_counts`, `statevector_summary`, and `execution_provenance`.
- **Q18: How are results serialized?**
  Canonical JSON serialization sorted by keys (`sort_keys=True`) with UTF-8 encoding.
- **Q19: How is execution provenance represented?**
  Includes `native_circuit_hash`, `backend_id`, `capability_hash`, `lowering_id`, `execution_mode`, `shot_count`, and `deterministic_execution_hash`.
- **Q20: How does Stage 4 consume the execution interface?**
  Stage 4 cloud adapters implement `ReferenceSimulatorProtocol` / `ExecutionEngineProtocol` for external cloud providers without modifying Stage 3.
- **Q21: How does Stage 5 consume results?**
  Stage 5 result verification engine consumes `SimulatorJobResult` to perform statistical chi-squared verification against expected probability distributions.
- **Q22: How does Stage 11 record execution lineage?**
  Execution completion events append immutable execution records to Stage 11 repository.
- **Q23: What constitutes execution failure?**
  Unsupported native gate, qubit out-of-bounds, unverified input circuit, or statevector numerical overflow (`EXECUTION_FAILURE`).
- **Q24: What constitutes inconclusive execution?**
  Execution encountered indeterminate numerical bounds or undersampled shot statistics (`INCONCLUSIVE`).
- **Q25: How is randomness controlled?**
  Sampled shot simulation uses explicit seed `seed_prng` in `SimulatorConfig`.
- **Q26: What constitutes a valid measurement distribution?**
  A dictionary mapping computational basis bitstrings to normalized probability floats $\sum P(k) = 1.0$.
- **Q27: What constitutes simulator determinism?**
  Identical native circuit + capability snapshot + simulator config $\rightarrow$ identical statevector & job hash.
- **Q28: What is the security/credential boundary?**
  Stage 3 operates 100% locally with 0 cloud credentials, API tokens, or network requests.
- **Q29: What is the hardware boundary?**
  `HARDWARE EXECUTION = 0%`. No physical hardware devices are contacted.
- **Q30: What is the cloud boundary?**
  `CLOUD EXECUTION = 0%`. No cloud APIs or SDKs are invoked.
