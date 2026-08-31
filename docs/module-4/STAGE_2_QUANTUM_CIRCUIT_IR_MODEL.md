# Stage 2 Specification — Quantum Circuit IR Model & Validator

**Module:** Module 4 — Quantum Circuit Synthesis  
**Stage:** Stage 2 — Quantum Circuit IR Model & Validator  
**Status:** IMPLEMENTATION COMPLETE / FROZEN  

---

## 1. Primary Objective & Architectural Mandate

Stage 2 specifies and implements `QuantumCircuitIR`, the first concrete, backend-independent Quantum Circuit Intermediate Representation in the compilation pipeline:

$$\text{RUTM} \longrightarrow \text{RUTM-IR} \longrightarrow \text{QTM-IR} \longrightarrow \mathbf{QuantumCircuitIR}$$

---

## 2. Core Circuit Data Model (`QuantumCircuitIR`)

```python
@dataclass
class QuantumCircuitIR:
    circuit_id: str
    registers: List[QubitRegister]
    gates: List[GateOperation] = field(default_factory=list)
    ancilla_declarations: List[AncillaDeclaration] = field(default_factory=list)
    input_register_ids: List[str] = field(default_factory=list)
    output_register_ids: List[str] = field(default_factory=list)
    provenance: Optional[CircuitProvenance] = None
    schema_version: str = "1.0.0"
```

---

## 3. Register & Qubit Identity Model

### 3.1 `QubitRegister`
- `register_id`: Unique string identifier.
- `register_type`: `STATE`, `TAPE`, `HEAD`, `HISTORY`, `STEP`, `STATUS`, or `ANCILLA`.
- `width`: Number of logical qubits in register ($> 0$).

### 3.2 `QubitRef`
- Canonical reference tuple `(register_id, index)`.
- Format string representation: `register_id[index]`.

---

## 4. Ancilla & Workspace Model

Workspace ancilla qubits are explicitly declared via `AncillaDeclaration`.
- **Status Classification:** `CLEAN` ($|0\rangle$) vs `DIRTY` (uncomputed).
- **Cleanliness Invariant:** All allocated workspace ancillas MUST have initial status `CLEAN` and expected final status `CLEAN`.

> [!IMPORTANT]
> **Logical History ($H$) vs Physical Ancilla:** Logical history $H$ is a component of classical configuration $C$, distinct from physical workspace ancillas. Physical workspace ancillas created during synthesis MUST undergo Bennett uncomputation back to $|0\rangle$.

---

## 5. Logical Gate Operation Model (`GateOperation`)

- `gate_type`: `X`, `CNOT`, or `TOFFOLI`.
- `target_qubit`: Target `QubitRef`.
- `control_qubits`: Tuple of control `QubitRefs`.
- `operation_index`: 0-based sequential ordering index.

### Canonical Arities
- Pauli-X ($X$): Arity 1 (0 controls, 1 target).
- CNOT ($\text{CNOT}$): Arity 2 (1 control, 1 target).
- Toffoli ($\text{TOFFOLI}$): Arity 3 (2 controls, 1 target).

---

## 6. Circuit Unitary Semantics & Ordering

Circuit semantics follow sequentialComposition:
$$U_C = U_{G_{m-1}} \dots U_{G_1} U_{G_0}$$
Each primitive gate operation is strictly unitary ($G^\dagger G = I$).

---

## 7. Boundaries & Prohibitions

1. **Measurement Boundary:** Measurement, reset, readout, and classical feedback operations are **FORBIDDEN** in Stage 2 logical `QuantumCircuitIR`.
2. **Classical Control Boundary:** Dynamic feed-forward and mid-circuit measurements are **FORBIDDEN**.
3. **Hardware Boundary:** Physical qubit routing, coupling graph SWAP insertion, native gate transpilation, and pulse control are **FORBIDDEN** (reserved for Module 5).
4. **QTM Translation Boundary:** Stage 2 defines the IR target structure; QTM transition synthesis belongs to Stage 3.

---

## 8. Validation Rules & 3-Level Validator

### Level 1: Structural Validation
- Schema version MUST equal `"1.0.0"`.
- Register IDs MUST be unique and widths positive.
- Gate arity MUST match gate type.
- Qubit indices MUST be within register bounds ($0 \le \text{index} < \text{width}$).
- Qubit distinctness: Control $\neq$ Target, Control1 $\neq$ Control2 within single gate.
- Operation indices MUST be sequential ($0, 1, \dots, m-1$).

### Level 2: Semantic Validation
- Input and output register IDs MUST exist in declared registers.
- All workspace ancillas MUST have `CLEAN` initial and final status.
- Provenance MUST contain non-empty program hash and QTM machine ID.

### Level 3: Mathematical Invariant Validation
- Primitive gates ($X$, $\text{CNOT}$, $\text{TOFFOLI}$) are structurally guaranteed unitary.
- No illegal qubit aliasing permitted.

---

## 9. Serialization & Lossless Round-Trip

Deterministic JSON serialization via `serialize_circuit_ir_to_json()` and `deserialize_circuit_ir_from_json()` enforces:
$$\text{deserialize}(\text{serialize}(C)) \equiv C$$
All field names, register orders, gate sequences, and provenance metadata are preserved losslessly.
