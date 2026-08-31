# Stage 1 Specification — Physical Circuit IR Model, Validator & Serialization

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Stage:** Stage 1 — Physical Circuit IR Model, Validator & Serialization  
**Status:** FORMALLY CLOSED / FROZEN  

---

## 1. Primary Objective

Stage 1 establishes the concrete data models, 3-level validator, and canonical JSON serializer/deserializer for the Module 5 **Physical Circuit Intermediate Representation (`PhysicalCircuitIR`)**.

---

## 2. Model Specifications

### 1. `PhysicalQubit`
- `node_id: int` (non-negative, unique physical execution node index).
- `device_id: str` (backend device identifier, defaults to `"reference_device"`).

### 2. `QubitMapping`
- Injective mapping $M_t: Q_L \to Q_P$ from logical `QubitRef` (`register_id[index]`) to physical node ID.
- Supports dynamic mapping evolution under physical routing operations via `apply_swap(node_a, node_b)` ($M(q_a)=p_a, M(q_b)=p_b \to M'(q_a)=p_b, M'(q_b)=p_a$).

### 3. `DeviceTopology`
- Abstract graph $G_P = (V_P, E_P)$ representing physical qubit node set $V_P$ and allowed two-qubit coupling edges $E_P$.
- Normalizes edges deterministically $(\min(u,v), \max(u,v))$. Forbids self-loops.

### 4. `PhysicalGateOperation`
- `gate_type: str` (non-empty native or primitive gate type string).
- `target_node: int` (physical target node ID).
- `control_nodes: Tuple[int, ...]` (tuple of physical control node IDs).
- `operation_index: int` (0-indexed sequential gate order).

### 5. `ExecutionProvenance`
- Upstream metadata chain (`source_rutm_program_hash`, `source_qtm_machine_id`, `logical_circuit_id`, `physical_circuit_id`, `backend_id`, `compiler_version`).

### 6. `PhysicalCircuitIR`
- Root AST containing `physical_circuit_id`, `source_logical_circuit_id`, `physical_qubits`, `gates`, `mapping`, `topology`, `schema_version = "1.0.0"`, `provenance`.

---

## 3. Validator Levels (`validate_physical_circuit_ir`)

- **Level 1 (Structural):** Validates schema version `"1.0.0"`, non-empty IDs, unique physical qubit node IDs, sequential 0..N-1 operation indices, non-empty gate types, control/target node distinctness, no duplicate control nodes.
- **Level 2 (Semantic):** Validates logical source circuit ID, physical node existence in `physical_qubits` for all gates, mapping entries, and topology nodes, mapping injectivity, topology edge connectivity for 2-qubit native operations, and non-empty provenance metadata.
- **Level 3 (Mathematical/Consistency):** Validates mapping injectivity, disjoint control-target node sets, and canonical gate arities ($X: 0, \text{CNOT}/\text{CZ}: 1, \text{TOFFOLI}: 2$).

---

## 4. Deterministic Canonical JSON Serialization

`serialize_physical_circuit_ir()` enforces byte-for-byte canonical top-level ordering:
1. `physical_circuit_id`
2. `source_logical_circuit_id`
3. `physical_qubits` (sorted by `node_id`)
4. `gates` (sorted by `operation_index`)
5. `mapping` (sorted lexicographically by `"register_id[index]"`)
6. `topology` (`nodes` sorted, `edges` normalized and sorted)
7. `schema_version`
8. `provenance`

**Round-trip Invariant:**
$$\text{deserialize}(\text{serialize}(C)) == C \quad \text{and} \quad \text{serialize}(\text{deserialize}(\text{serialize}(C))) == \text{serialize}(C)$$

---

## 5. Explicit Non-Goals for Stage 1

- Automatic qubit allocation algorithms.
- SWAP routing search algorithms.
- Hardware native gate translation engines.
- External hardware SDK integration / remote submission.
- Noise simulation.
- Modifying Modules 1–4.
