# Stage 4 Specification — Hardware Native Gate Translation & Device Adapter Layer

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Stage:** Stage 4 — Hardware Native Gate Translation & Device Adapter Layer  
**Status:** FORMALLY CLOSED / FROZEN  

---

## 1. Primary Objective

Stage 4 implements offline physical-to-native gate translation and device adapter abstraction for Module 5. It transforms a `PhysicalCircuitIR` (from Stage 3) into a backend-native `NativeCircuitIR` under a declared `BackendCapabilityModel` and `BackendAdapter`:

$$\text{PhysicalCircuitIR} + \text{BackendCapabilityModel} \xrightarrow{\text{BackendAdapter} + \text{GateDecompositionRegistry}} \text{NativeCircuitIR}$$

---

## 2. Absolute Boundary Isolation

- **100% OFFLINE Translation Only:** Stage 4 performs static circuit translation and verification in-process.
- **NO Hardware Execution:** Does NOT submit jobs to QPUs, invoke remote APIs, manage credentials, or perform hardware execution.
- **NO Stage 3 Rerouting:** Does NOT modify qubit mappings or perform SWAP routing (Stage 3 owns topology placement & routing).
- **NO Hardware Noise Modeling:** Hardware noise simulation remains strictly deferred.

---

## 3. Five Required Layers

1. **Backend Capability Matching:** Queries `BackendCapabilityModel` and `BackendAdapter` to verify supported gates, arities, and topology constraints.
2. **Native Gate Vocabulary Resolution:** Maps physical gates into native gate definitions (`DIRECT_NATIVE`, `DECOMPOSED`, `UNSUPPORTED`).
3. **Gate Decomposition & Translation:** Uses `GateDecompositionRegistry` to decompose non-native gates (e.g. `SWAP` $\to$ 3 `CNOT`s, `CNOT` on CZ-native $\to$ `H, CZ, H`, `TOFFOLI` $\to$ 6-CNOT sequence).
4. **Backend Adapter Abstraction (`BackendAdapter`):** Provides vendor-neutral adapter contract and concrete `ReferenceBackendAdapter`.
5. **3-Level Semantic Verification (`NativeCircuitVerifier`):**
   - **Level 1 (Symbolic):** Gate sequence correspondence, operands, parameters, operation order.
   - **Level 2 (State-Vector):** Superposition amplitude simulation. $\| U_\text{physical} |\psi\rangle - U_\text{native} |\psi\rangle \| < 10^{-12}$, norm preservation, and adjoint equivalence.
   - **Level 3 (Operator Matrix Unitarity):** $\| U_\text{physical} - U_\text{native} \| < 10^{-12}$, left unitarity $\| U_\text{native}^\dagger U_\text{native} - I \| < 10^{-12}$, right unitarity $\| U_\text{native} U_\text{native}^\dagger - I \| < 10^{-12}$.

---

## 4. Native Vocabulary Closure Invariant

Every operation $G \in \text{NativeCircuitIR}$ MUST belong to the target backend's native vocabulary:

$$\forall G \in \text{NativeCircuitIR}: G \in \text{BackendNativeGateVocabulary}$$

No abstract or unresolved logical/physical gate may remain.

---

## 5. Deterministic JSON Serialization

`serialize_native_circuit_ir()` enforces canonical top-level ordering:
1. `circuit_id`
2. `backend_id`
3. `backend_version`
4. `qubits` (sorted)
5. `native_operations` (sorted by `operation_index`)
6. `input_mapping`
7. `output_mapping`
8. `schema_version = "1.0.0"`
9. `provenance`

**Round-trip Invariant:**
$$\text{deserialize}(\text{serialize}(N)) == N \quad \text{and} \quad \text{serialize}(\text{deserialize}(\text{serialize}(N))) == \text{serialize}(N)$$

---

## 6. Upstream Provenance Preservation

`ExecutionProvenance` retains complete end-to-end traceability:
- `source_rutm_program_hash`: Propagated from Module 4 input.
- `source_qtm_machine_id`: Propagated from Module 4 input.
- `logical_circuit_id`: Input logical circuit ID.
- `physical_circuit_id`: Stage 3 physical circuit ID.
- `backend_id`: Target backend identifier.
- `compiler_version`: `"0.5.0-alpha"`.
