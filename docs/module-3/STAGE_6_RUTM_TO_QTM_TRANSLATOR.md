# Stage 6 Specification & Architecture — RUTM-IR $\to$ QTM-IR Translator ($T_{RQ}$)

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 6 — RUTM-IR $\to$ QTM-IR Translator ($T_{RQ}$)  
**Status:** FORMALLY CLOSED / FROZEN (FINAL MICRO CLOSURE CORRECTION COMPLETE)  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md), [`STAGE_2_QTM_STATE_MODEL.md`](STAGE_2_QTM_STATE_MODEL.md), [`STAGE_3_QTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_QTM_OPERATIONAL_SEMANTICS.md), [`STAGE_4_UNITARY_EQUIVALENCE_PROOF.md`](STAGE_4_UNITARY_EQUIVALENCE_PROOF.md), [`STAGE_5_QTM_IR_MODEL_AND_VALIDATOR.md`](STAGE_5_QTM_IR_MODEL_AND_VALIDATOR.md)  

---

## 1. Stage 6 Purpose & Architectural Role

Stage 6 implements the compiler translation engine **$T_{RQ}$** converting reversible machine descriptions (`RUTM-IR` or `RUTMProgram` and `RUTMConfiguration`) from Module 2 into validated Quantum Turing Machine Intermediate Representation (`QTMIRModel`) objects in Module 3.

```
 Module 2 (RUTM-IR)
    (P, C_R)
        |
        | T_RQ (Stage 6)
        v
 Module 3 (QTM-IR) ---> validate_qtm_ir() ---> Stage 7 (QTM Execution Engine)
```

> [!IMPORTANT]
> **Stage 6 Non-Goals:**  
> Translator $T_{RQ}$ performs semantic lifting. It strictly excludes:
> - Quantum circuit synthesis (qubits, Toffoli, CNOT, Hadamard, X gates).
> - Hardware target transpilation.
> - Quantum execution or measurement (Stage 7).

---

## 2. Mathematical Foundation & Translator Notation

The translator notation is defined as:
$$T_{RQ} : \text{RUTM-IR} \to \text{QTM-IR}$$

The central mathematical relation established in Stage 4 and operationally preserved by $T_{RQ}$ is:
$$U_P \circ \iota = \iota \circ R_P$$

and for the adjoint operator:
$$U_P^\dagger \circ \iota = \iota \circ R_P^{-1}$$

where $\iota(C_R) = |C_R\rangle$ maps 7-tuple RUTM configurations $C_R = (q, T, h, H, k, \text{halted}, \text{error})$ into Hilbert space basis vectors $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$.

---

## 3. Final Micro Closure Correction — Error Reverse Semantics Audit

During the Final Micro Closure Correction, the reverse transition mapping generation was audited to eliminate any reliance on `forward_mapping` fallback loops:

1. **Previous Behavior & Insufficiency:** Previously, if `reverse_step_rutm` encountered an error or non-standard configuration, a fallback loop scanned `forward_mapping` (`for s, t in forward_mapping.items(): if t == target: predecessor = s`). This was semantically insufficient because it derived reverse semantics from forward mapping rather than authoritative Module 2 $R_P^{-1}$.
2. **Authoritative Module 2 Inverse Semantics:** Module 2 `reverse_step_rutm()` explicitly defines $R_P^{-1}(C_\text{error}) = C_\text{error}$ as an error fixed point (Case A).
3. **Corrected Behavior & Zero Fallback Rule:** $T_{RQ}$ directly invokes Module 2 `reverse_step_rutm(cfg, utm_prog)` for all configurations. Error states preserve fixed point $R_P^{-1}(C_\text{error}) = C_\text{error}$. Zero `forward_mapping` fallbacks exist. Undefined or non-closed reverse transitions raise `RUTMToQTMTranslationError` explicitly.

---

## 4. Input & Output Contracts

### 4.1 Input Contract
Consumes frozen Module 2 canonical types:
- `program`: `Union[RUTM_IR, UTMProgram]`
- `initial_config`: `Optional[RUTMConfiguration]`
- `custom_domain`: `Optional[List[RUTMConfiguration]]`

### 4.2 Output Contract
Produces a canonical `QTMIRModel` instance containing:
- `version`: `"1.0.0"`
- `machine_id`: String identifier
- `basis_states`: `Dict[str, QTMIRBasisState]`
- `initial_state_vector`: `QTMIRStateVector` ($|\psi_0\rangle = |C_0\rangle$)
- `transition_mapping`: `QTMIRTransitionMapping` ($R_P$ and $R_P^{-1}$)
- `matrix_representation`: `Optional[QTMIRMatrixRepresentation]` ($[U_P]_{N \times N}$)
- `provenance`: `QTMIRProvenance`

---

## 5. Configuration & Basis Identity Lifting

### 5.1 Configuration Lifting
Each 7-tuple configuration $C_R = (q, T, h, H, k, \text{halted}, \text{error})$ is lifted into `QTMIRBasisState`:
- `current_state` $= q$
- `tape` $= T$
- `head_pos` $= h$
- `history` $= H$ (auxiliary sequence strictly preserved)
- `step_count` $= k$
- `halted` $= \text{halted}$
- `error` $= \text{error}$

### 5.2 Deterministic Canonical Basis Identity
Canonical basis ID is computed via SHA-256 over configuration 7-tuple:
$$\text{compute\_canonical\_basis\_id}(C_1) == \text{compute\_canonical\_basis\_id}(C_2) \iff C_1 == C_2$$

---

## 6. Forward & Reverse Transition Mappings

For every configuration $C \in D$:
- **Forward Mapping ($R_P$):** $\text{forward\_mapping}[\text{basis\_id}(C)] = \text{basis\_id}(R_P(C))$
- **Reverse Mapping ($R_P^{-1}$):** $\text{reverse\_mapping}[\text{basis\_id}(C')] = \text{basis\_id}(R_P^{-1}(C'))$

**Bijectivity Invariants:**
$$\text{dom}(R_P) = D, \quad \text{ran}(R_P) = D, \quad \text{dom}(R_P^{-1}) = D, \quad \text{ran}(R_P^{-1}) = D$$
$$R_P^{-1} \circ R_P = \text{id}_D, \quad R_P \circ R_P^{-1} = \text{id}_D$$

---

## 7. Finite Matrix Representation & Two-Sided Unitarity

When $D$ is finite ($N = |D|$), $T_{RQ}$ constructs $[U_P] \in \mathbb{C}^{N \times N}$ in canonical sorted basis order:
$$[U_P]_{i,j} = \begin{cases} 1.0 & \text{if } R_P(B_j) = B_i \\ 0.0 & \text{otherwise} \end{cases}$$

The matrix is guaranteed to satisfy permutation row/col structure and two-sided unitarity:
$$[U_P]^\dagger [U_P] = I_{N \times N} \quad \text{and} \quad [U_P] [U_P]^\dagger = I_{N \times N}$$

---

## 8. Provenance & Deterministic Source Hashing

- `source_rutm_program_hash`: Deterministic SHA-256 hash of transitions, alphabet, and states.
- `source_module`: `"Module 2 (RUTM-IR)"`
- `stage`: `"Stage 6 (Translator T_RQ)"`
- `compiler_version`: `"0.3.0-alpha"`
- `semantic_relation`: `"Canonical QTM Lifting (U_P ∘ ι = ι ∘ R_P)"`

---

## 9. Validation Gate Policy

Upon building `qtm_ir = model`, $T_{RQ}$ executes:
```python
val_res = validate_qtm_ir(model)
if not val_res.valid:
    raise RUTMToQTMTranslationError(...)
```
> [!CAUTION]
> If validation fails, $T_{RQ}$ fails explicitly. It does **NOT** auto-repair malformed models or insert missing states.

---

## 10. Stage 6 Invariants ($I_1 \dots I_{15}$)

- **$I_1$ (Configuration Identity Preservation):** Complete 7-tuple $C_R$ preserved.
- **$I_2$ (History Preservation):** $H$ sequence preserved in `QTMIRBasisState`.
- **$I_3$ (Basis Identity Determinism):** Basis ID calculation is deterministic.
- **$I_4$ (Initial-State Preservation):** $|\psi_0\rangle = |C_0\rangle$ with amplitude $1.0 + 0i$.
- **$I_5$ (Forward Transition Preservation):** Forward mapping matches actual $R_P$.
- **$I_6$ (Reverse Transition Preservation):** Reverse mapping matches actual $R_P^{-1}$.
- **$I_7$ (Totality Preservation):** $\text{dom}(R_P) = D$ and $\text{dom}(R_P^{-1}) = D$.
- **$I_8$ (Injectivity Preservation):** Mappings are collision-free.
- **$I_9$ (Surjectivity Preservation):** $\text{ran}(R_P) = D$ and $\text{ran}(R_P^{-1}) = D$.
- **$I_{10}$ (Reverse Composition):** $R_P^{-1} \circ R_P = \text{id}_D$ and $R_P \circ R_P^{-1} = \text{id}_D$.
- **$I_{11}$ (Matrix Permutation Correspondence):** Matrix rows/cols have exactly one 1.0.
- **$I_{12}$ (Matrix Unitarity):** $[U_P]^\dagger [U_P] = I_N$ and $[U_P] [U_P]^\dagger = I_N$.
- **$I_{13}$ (Provenance Integrity):** Program hash and canonical semantic relation populated.
- **$I_{14}$ (Serialization Preservation):** Model survives JSON round trip without loss.
- **$I_{15}$ (Semantic Commuting Relation):** $U_P \circ \iota = \iota \circ R_P$ verified.

---

## 11. Verification & Regression Status

- **Module 3 Stage 6 Unit Tests:** 21 / 21 PASS (`tests/module3/test_stage6_rutm_to_qtm.py`)
- **Module 3 Total Unit Tests:** 76 / 76 PASS (16 Stage 2 + 15 Stage 3 + 10 Stage 4 + 14 Stage 5 + 21 Stage 6)
- **Module 1 Regression:** 79 / 79 PASS
- **Module 2 Regression:** 155 / 155 PASS
- **Production Files Created / Updated:**
  - [`src/module3/translator/__init__.py`](../../src/module3/translator/__init__.py)
  - [`src/module3/translator/rutm_to_qtm.py`](../../src/module3/translator/rutm_to_qtm.py)
  - [`tests/module3/test_stage6_rutm_to_qtm.py`](../../tests/module3/test_stage6_rutm_to_qtm.py)
  - [`src/module3/__init__.py`](../../src/module3/__init__.py)
  - [`docs/module-3/STAGE_6_RUTM_TO_QTM_TRANSLATOR.md`](STAGE_6_RUTM_TO_QTM_TRANSLATOR.md)
