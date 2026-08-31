# Stage 5 Specification & Architecture — QTM-IR Model, Semantic Validator & Canonical Serialization

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 5 — QTM-IR Model & Validator  
**Status:** FORMALLY CLOSED / FROZEN (MICRO CLOSURE CORRECTION COMPLETE)  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md), [`STAGE_2_QTM_STATE_MODEL.md`](STAGE_2_QTM_STATE_MODEL.md), [`STAGE_3_QTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_QTM_OPERATIONAL_SEMANTICS.md), [`STAGE_4_UNITARY_EQUIVALENCE_PROOF.md`](STAGE_4_UNITARY_EQUIVALENCE_PROOF.md)  

---

## 1. Executive Summary & Architectural Role

Stage 5 converts the mathematically established Quantum Turing Machine abstraction from Stages 1–4 into a canonical, structured Intermediate Representation (**QTM-IR**), complete with an observational, non-mutating semantic validation engine (`validate_qtm_ir`) and deterministic JSON serialization.

```
       Stage 6 (T_RQ)
RUTM-IR --------------> QTM-IR (Stage 5 Contract) --------------> Stage 7 (QTM Engine)
                             |
                             v
                     validate_qtm_ir()
```

> [!IMPORTANT]
> **Stage 5 Architectural Boundary:**  
> QTM-IR defines the intermediate representation contract consumed and produced by translator Stage 6, executed by simulator Stage 7, and verified by equivalence gate Stage 8.  
> Stage 5 does **NOT** implement the translator (`T_RQ`), execution engine, or quantum gate synthesis.

---

## 2. QTM-IR Canonical Data Model

The data model is implemented under [`src/module3/qtm_ir/model.py`](../../src/module3/qtm_ir/model.py):

### 2.1 `QTMIRComplexNumber`
Canonical encoding of complex amplitudes $\alpha = a + bi$:
```json
{
  "real": 0.7071067811865475,
  "imag": 0.0
}
```

### 2.2 `QTMIRBasisState` (Isolated Configuration Identity Completeness)
Canonical reference for computational basis vector $|C_R\rangle$, preserving the full 7-tuple RUTM configuration $(q, T, h, H, k, \text{halted}, \text{error})$:
```json
{
  "basis_id": "b_iso",
  "current_state": "q_step1",
  "tape": { "0": "1" },
  "head_pos": 0,
  "history": [
    {
      "direction": "R",
      "overwritten_symbol": "0",
      "prev_state": "q_start"
    }
  ],
  "step_count": 1,
  "halted": false,
  "error": null
}
```
> [!NOTE]
> **Isolated Semantic Configuration Identity:** Two configurations $C_1$ and $C_2$ having identical `basis_id`, `current_state`, `tape`, `head_pos`, `step_count`, `halted`, and `error` but differing ONLY in `history` ($H_1 \neq H_2$) satisfy $C_1 \neq C_2$ and $\iota(C_1) \neq \iota(C_2)$. History content is independently preserved through dictionary and JSON serialization round-trips.

### 2.3 `QTMIRStateVector`
Sparse representation of superposition state $|\psi\rangle = \sum \alpha_C |C_R\rangle$:
```json
{
  "amplitudes": {
    "b0": { "real": 0.7071067811865475, "imag": 0.0 },
    "b1": { "real": 0.0, "imag": 0.7071067811865475 }
  },
  "tolerance": 1e-12,
  "is_normalized": true
}
```

### 2.4 `QTMIRTransitionMapping` (Complete Forward & Reverse Mapping)
Complete permutation transition specification $R_P : \mathcal{C}_R \to \mathcal{C}_R$ and complete reverse transition mapping $R_P^{-1} : \mathcal{C}_R \to \mathcal{C}_R$:
```json
{
  "forward_mapping": { "b0": "b1", "b1": "b2", "b2": "b0" },
  "reverse_mapping": { "b1": "b0", "b2": "b1", "b0": "b2" },
  "is_bijective": true
}
```

### 2.5 `QTMIRMatrixRepresentation`
Optional finite $N \times N$ matrix representation $[U_P]$:
```json
{
  "basis_order": ["b0", "b1", "b2"],
  "matrix": [
    [ { "real": 0.0, "imag": 0.0 }, { "real": 0.0, "imag": 0.0 }, { "real": 1.0, "imag": 0.0 } ],
    [ { "real": 1.0, "imag": 0.0 }, { "real": 0.0, "imag": 0.0 }, { "real": 0.0, "imag": 0.0 } ],
    [ { "real": 0.0, "imag": 0.0 }, { "real": 1.0, "imag": 0.0 }, { "real": 0.0, "imag": 0.0 } ]
  ],
  "dimension": 3
}
```

### 2.6 `QTMIRProvenance` (Exact Canonical Relation)
Deterministic compiler provenance metadata back to Module 2 RUTM source:
```json
{
  "source_rutm_program_hash": "8265bad0ba8f0f2135f12246b514ac2afa6fa3cadb4c525e131b99119598f081",
  "source_module": "Module 2 (RUTM-IR)",
  "stage": "Stage 5 (QTM-IR Model)",
  "compiler_version": "0.3.0-alpha",
  "semantic_relation": "Canonical QTM Lifting (U_P ∘ ι = ι ∘ R_P)"
}
```
> [!IMPORTANT]
> **Exact Relation Rule:** `provenance.semantic_relation` MUST equal `CANONICAL_SEMANTIC_RELATION = "Canonical QTM Lifting (U_P ∘ ι = ι ∘ R_P)"` exactly. Substring or partial matches are rejected.

---

## 3. Observational Semantic Validator (`validate_qtm_ir`)

Implemented under [`src/module3/qtm_ir/validator.py`](../../src/module3/qtm_ir/validator.py).

> [!CAUTION]
> **Observational Policy:** Validation is strictly observational and non-mutating. It does **NOT** auto-repair malformed state vectors, auto-normalize amplitudes, or alter reverse transition mappings.

### 3.1 Validation Levels
1. **Level 1 (Structural):** Validates class types, required attributes, non-empty IDs, and schema version match (`QTM_IR_VERSION = "1.0.0"`).
2. **Level 2 (Semantic):** Validates basis state ID consistency, state vector amplitude key references in `basis_states`, terminal state consistency, and exact canonical provenance contract (`semantic_relation == CANONICAL_SEMANTIC_RELATION`).
3. **Level 3 (Mathematical Invariants):**
   - State vector norm preservation $\| |\psi_0\rangle \| = 1.0 \pm \text{tol}$.
   - Amplitude numeric validity (rejects `NaN` and `Inf`).
   - Forward & reverse total bijectivity over declared basis domain $D$:
     - Forward mapping: $\text{dom}(R_P) = D, \text{ran}(R_P) = D$, collision-free.
     - Reverse mapping: $\text{dom}(R_P^{-1}) = D, \text{ran}(R_P^{-1}) = D$, collision-free.
     - Both composition identities: $R_P^{-1} \circ R_P = \text{id}_D$ AND $R_P \circ R_P^{-1} = \text{id}_D$.
   - Two-sided matrix unitarity: verifies square matrix shape, permutation row/col structure (exactly one 1.0 per row/col), left unitarity ($[U_P]^\dagger [U_P] = I_{N \times N}$), AND right unitarity ($[U_P] [U_P]^\dagger = I_{N \times N}$).

### 3.2 Structured Diagnostic Error Codes (`DiagnosticCode`)
- `QTM_SCHEMA_INVALID`
- `QTM_VERSION_UNSUPPORTED`
- `QTM_BASIS_INVALID`
- `QTM_AMPLITUDE_INVALID`
- `QTM_DOMAIN_NOT_CLOSED`
- `QTM_TRANSITION_NOT_BIJECTIVE`
- `QTM_MATRIX_NOT_SQUARE`
- `QTM_MATRIX_NOT_PERMUTATION`
- `QTM_MATRIX_NOT_UNITARY`
- `QTM_INITIAL_STATE_INVALID`
- `QTM_TERMINAL_STATE_INVALID`
- `QTM_PROVENANCE_INVALID`

---

## 4. Deterministic Canonical Serialization

Implemented under [`src/module3/qtm_ir/serialization.py`](../../src/module3/qtm_ir/serialization.py).

Provides deterministic sorting across:
- `basis_states` sorted by `basis_id`.
- `tape` dictionaries sorted by integer key index.
- `history` tuples reconstructed into `HistoryRecord` objects.
- `initial_state_vector.amplitudes` sorted by `basis_id`.
- `transition_mapping.forward_mapping` sorted by source `basis_id`.
- `transition_mapping.reverse_mapping` sorted by target `basis_id`.

**Round-Trip Semantic Invariant:**
$$\text{deserialize\_qtm\_ir}(\text{serialize\_qtm\_ir}(M)) == M$$

---

## 5. Stage 6 Interface Contract

Stage 6 (`RUTM-IR` $\to$ `QTM-IR` Translator $T_{RQ}$) MUST satisfy the following operational contract:
1. Accept valid `RUTMProgram` / `RUTMConfiguration` objects from Module 2.
2. Construct a valid `QTMIRModel` instance populated with basis states (including full `history`), initial state vector $|\psi_0\rangle = |C_0\rangle$, complete forward and reverse bijective transition mappings $R_P$ and $R_P^{-1}$, and provenance metadata (`source_rutm_program_hash`, exact `CANONICAL_SEMANTIC_RELATION`).
3. Call `validate_qtm_ir(qtm_ir)` to verify that `valid == True` prior to returning QTM-IR.

---

## 6. Implementation Non-Goals

Stage 5 strictly excludes:
- `RUTM-IR` $\to$ `QTM-IR` translation algorithms (Stage 6).
- State vector evolution execution loop / simulator (Stage 7).
- Reversible-to-quantum equivalence verification gate (Stage 8).
- Quantum circuit synthesis, qubit registers, Toffoli/CNOT/Hadamard gates (Module 4).

---

## 7. Verification & Regression Status

- **Module 3 Stage 5 Unit Tests:** 14 / 14 PASS (`tests/module3/test_stage5_qtm_ir.py`)
- **Module 3 Total Unit Tests:** 55 / 55 PASS (16 Stage 2 + 15 Stage 3 + 10 Stage 4 + 14 Stage 5)
- **Module 1 Regression:** 79 / 79 PASS
- **Module 2 Regression:** 155 / 155 PASS
- **Production Files Updated:**
  - [`src/module3/qtm_ir/__init__.py`](../../src/module3/qtm_ir/__init__.py)
  - [`src/module3/qtm_ir/model.py`](../../src/module3/qtm_ir/model.py)
  - [`src/module3/qtm_ir/validator.py`](../../src/module3/qtm_ir/validator.py)
  - [`src/module3/qtm_ir/serialization.py`](../../src/module3/qtm_ir/serialization.py)
  - [`tests/module3/test_stage5_qtm_ir.py`](../../tests/module3/test_stage5_qtm_ir.py)
  - [`src/module3/__init__.py`](../../src/module3/__init__.py)
