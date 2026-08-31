# Stage 3 Specification — Physicalization Layer & SWAP Routing Engine

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Stage:** Stage 3 — Physicalization Layer & PhysicalCircuitIR Model (Mapping, Topology Enforcement, SWAP Routing)  
**Status:** FORMALLY CLOSED / FROZEN  

---

## 1. Primary Objective

Stage 3 transforms a logically valid `QuantumCircuitIR` from Module 4 into a topology-compatible `PhysicalCircuitIR` by enforcing device topology constraints and inserting explicit physical `SWAP` operations where necessary:

$$\text{QuantumCircuitIR} + \text{DeviceTopology} \xrightarrow{\text{InitialMapping } M_0 + \text{SWAP Routing}} \text{PhysicalCircuitIR} + \text{RoutingTrace}$$

---

## 2. Core Architecture & Workflow

1. **Logical Qubit Discovery (`InitialMapper.discover_logical_qubits`):** Discovers all logical qubit references $Q_L$ in canonical register order (`register_id`, `index`).
2. **Deterministic Initial Allocation (`InitialMapper.allocate`):** Allocates injective mapping $M_0: q_i \mapsto p_i$ (sorted topology node $i$). Validates $|Q_L| \le |V_P|$.
3. **Topology Violation Detection & SWAP Routing (`ShortestPathRouter`):**
   - For 1-qubit gates: emit physical gate directly on $p = M_t(q)$.
   - For 2-qubit gates $(q_a, q_b)$ on $(p_a, p_b)$:
     - If $\text{is\_connected}(p_a, p_b)$ is True: emit physical gate directly.
     - Else: compute deterministic shortest path $p_a = v_0, v_1, \dots, v_k = p_b$. Insert physical `SWAP(v_i, v_{i+1})` gates along path, updating $M_t \to M_{t+1}$ dynamically via `QubitMapping.apply_swap()`. Emit the physical gate on adjacent nodes $(v_{k-1}, v_k)$.
4. **Auditable Tracing (`RoutingTrace` & `RoutingEvent`):** Records operation indices, logical operands, physical operands before/after, selected path, and inserted SWAPs.
5. **Post-Routing Verification (`SemanticPreservationVerifier`):**
   - Verifies input `QuantumCircuitIR` was not mutated.
   - Verifies $M_t$ injectivity at every step.
   - Verifies all physical 2-qubit gates in the generated `PhysicalCircuitIR` satisfy device topology connectivity.
   - Runs Stage 1 `validate_physical_circuit_ir()`.

---

## 3. Deterministic Routing & Tie-Breaking Policy

- **Path Algorithm:** Breadth-First Search (BFS) over $G_P = (V_P, E_P)$.
- **Tie-Breaking Rule:** Among all shortest paths of minimum hop count, the router deterministically selects the **lexicographically smallest node sequence tuple**, e.g., path `(0, 1, 3)` is preferred over `(0, 2, 3)`.
- **Result:** 100% process-deterministic and byte-for-byte reproducible physicalization.

---

## 4. Upstream Provenance Preservation

`ExecutionProvenance` retains complete traceability:
- `source_rutm_program_hash`: Propagated from Module 4 input.
- `source_qtm_machine_id`: Propagated from Module 4 input.
- `logical_circuit_id`: Input circuit ID.
- `physical_circuit_id`: `f"phys_{logical_circuit_id}"`.
- `backend_id`: `"STAGE_3_PHYSICALIZATION_AND_SWAP_ROUTING"`.

---

## 5. Explicit Non-Goals for Stage 3 (Stage 4 Boundary)

- Native hardware gate translation (e.g. converting CNOT to CZ or Rz).
- Backend device execution or remote job submission.
- Noise simulation or readout mitigation.
- Arbitrary non-canonical routing heuristic optimization.

Stage 3 is strictly responsible for: **Logical-to-Physical Mapping, Topology Enforcement, and SWAP Routing**.
