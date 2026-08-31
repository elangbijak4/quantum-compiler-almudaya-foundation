# Stage 2 Specification — Backend Abstraction & Capability Model Framework

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Stage:** Stage 2 — Backend Abstraction & Capability Model Framework  
**Status:** FORMALLY CLOSED / FROZEN  

---

## 1. Primary Objective

Stage 2 establishes a backend-independent capability abstraction layer for Module 5. It provides a formal model describing what a backend **CAN** support (`BackendCapabilityModel`) and evaluates whether a `PhysicalCircuitIR` is compatible with a backend (`validate_backend_compatibility()`) without executing or routing the circuit:

$$\text{PhysicalCircuitIR} + \text{BackendCapabilityModel} \longrightarrow \text{BackendCompatibilityResult}$$

---

## 2. Core Model Architecture (`BackendCapabilityModel`)

1. **`BackendIdentity`:** Vendor-neutral identity (`backend_id`, `backend_name`, `backend_version`, `backend_type` enum).
2. **`QubitCapacity`:** Maximum physical qubit capacity bound (`max_qubits`) and optional active node set (`active_qubits`).
3. **`BackendTopologyCapability`:** Abstract connectivity graph $G_B = (V_B, E_B)$ supporting `supports_qubit(node_id)` and `supports_connection(u, v)`.
4. **`GateCapability` & `GateConstraint`:** Supported physical gate vocabulary (`gate_type`, `arity`, `supported`, `native`) and declarative constraints (`requires_connectivity`, `max_controls`).
5. **`MeasurementCapability`:** Readout operational capabilities (`supports_measurement`, `supports_shots`, `supports_counts`, `supports_mid_circuit_measurement`, `supports_reset`).
6. **`ExecutionCapability`:** Execution mode capabilities (`supports_statevector`, `supports_shots`, `supports_sampling`, `supports_async_execution`, `supports_batch_execution`, `supports_deterministic_seed`).
7. **`NumericalCapability`:** Precision and mathematical tolerance settings (`supports_complex_amplitudes`, `numerical_precision`, `deterministic_mode`, `epsilon = 1e-12`).
8. **`BackendCapabilityProvenance`:** Metadata tracking capability model generation.

---

## 3. Pure Query & Compatibility Validation APIs

### 1. Pure Capability Query API
- `supports_gate(gate_type) -> bool`
- `supports_gate_arity(gate_type, arity) -> bool`
- `supports_qubit(node_id) -> bool`
- `supports_connection(u, v) -> bool`
- `supports_measurement() -> bool`
- `supports_shots() -> bool`
- `supports_statevector() -> bool`
- `supports_sampling() -> bool`
- `supports_gate_on_nodes(gate_type, nodes) -> bool`

### 2. Compatibility Evaluation API (`validate_backend_compatibility`)
Determines compatibility between a `PhysicalCircuitIR` and a `BackendCapabilityModel`:
- **Qubit Capacity Check:** Circuit qubit count $\le$ `max_qubits`.
- **Physical Node Check:** All physical node IDs exist in backend topology.
- **Gate Support Check:** All circuit gates exist in backend capability vocabulary.
- **Arity Match Check:** Circuit gate arity matches backend gate arity.
- **Topology Edge Check:** All 2-node physical gates satisfy `supports_connection(u, v)`.

---

## 4. Canonical Deterministic JSON Serialization

`serialize_backend_capabilities()` enforces byte-for-byte canonical top-level ordering:
1. `identity`
2. `qubit_capacity`
3. `topology` (`nodes` sorted, `edges` normalized and sorted)
4. `gate_capabilities` (sorted by gate_type key)
5. `gate_constraints` (sorted by gate_type key)
6. `measurement`
7. `execution`
8. `numerical`
9. `schema_version = "1.0.0"`
10. `provenance`

**Round-trip Invariant:**
$$\text{deserialize}(\text{serialize}(B)) == B \quad \text{and} \quad \text{serialize}(\text{deserialize}(\text{serialize}(B))) == \text{serialize}(B)$$

---

## 5. Vendor-Neutral Reference Capability Profile

`create_reference_simulator_capabilities(max_qubits=32)` provides the standard vendor-neutral `reference_simulator` profile:
- `backend_id`: `"reference_simulator"`
- `backend_type`: `BackendType.REFERENCE_SIMULATOR`
- 32-qubit fully connected topology.
- Supported gates: `X`, `Y`, `Z`, `H`, `S`, `T`, `SX`, `CNOT`, `CZ`, `SWAP`, `TOFFOLI`.
- Full support for state-vector simulation, measurement, sampling, and shots.

---

## 6. Explicit Non-Goals for Stage 2

- Automatic logical-to-physical qubit allocation.
- SWAP routing search or shortest-path routing.
- Native gate decomposition or translation.
- Vendor SDK integration / remote hardware submission.
- Noise simulation.
- Circuit execution or state-vector simulation.
- Modifying Modules 1–4 or Stage 1.
