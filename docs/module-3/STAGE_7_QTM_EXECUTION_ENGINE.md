# Stage 7 Specification & Architecture — QTM Execution Engine & State Vector Evolution

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 7 — QTM Execution Engine & State Vector Evolution  
**Status:** FORMALLY CLOSED / FROZEN  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md), [`STAGE_2_QTM_STATE_MODEL.md`](STAGE_2_QTM_STATE_MODEL.md), [`STAGE_3_QTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_QTM_OPERATIONAL_SEMANTICS.md), [`STAGE_4_UNITARY_EQUIVALENCE_PROOF.md`](STAGE_4_UNITARY_EQUIVALENCE_PROOF.md), [`STAGE_5_QTM_IR_MODEL_AND_VALIDATOR.md`](STAGE_5_QTM_IR_MODEL_AND_VALIDATOR.md), [`STAGE_6_RUTM_TO_QTM_TRANSLATOR.md`](STAGE_6_RUTM_TO_QTM_TRANSLATOR.md)  

---

## 1. Stage 7 Purpose & Architectural Role

Stage 7 implements the **QTM Execution Engine** in Module 3. Its purpose is to execute validated Quantum Turing Machine Intermediate Representation (`QTMIRModel`) objects, evolving state vectors according to the unitary transition operator $U_P$ over the Hilbert space $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$.

```
 QTM-IR (Validated Model)
        |
        v
 QTM Execution Engine (Stage 7) ---> validate_qtm_ir() gate
        |
        v
 Quantum State Evolution Trace (|ψ(0)>, |ψ(1)>, ..., |ψ(T)>)
```

> [!IMPORTANT]
> **Stage 7 Scope Boundaries:**  
> Stage 7 executes QTM-IR state vectors. It strictly **DOES NOT** perform:
> - Quantum circuit synthesis (Hadamard, Toffoli, CNOT, X gates).
> - Born-rule measurement or wave-function collapse.
> - Hardware target transpilation.
> - RUTM $\to$ QTM translation (handled by Stage 6).

---

## 2. Mathematical Foundation & Fundamental Evolution Law

The fundamental evolution equation implemented by the engine is:
$$|\psi(t+1)\rangle = U_P |\psi(t)\rangle \implies |\psi(t)\rangle = U_P^t |\psi(0)\rangle$$

For a general sparse superposition:
$$|\psi\rangle = \sum_i \alpha_i |B_i\rangle$$

the unitary transition operator $U_P = \sum_C |R_P(C)\rangle\langle C|$ acts linearly:
$$U_P |\psi\rangle = \sum_i \alpha_i |R_P(B_i)\rangle$$

If multiple source basis states map to target $B_j$, amplitudes accumulate linearly:
$$\beta_j = \sum_{i : R_P(B_i) = B_j} \alpha_i$$

### Norm & Inner Product Preservation
For any normalized state $\|\psi\| = 1$:
$$\|U_P \psi\| = 1 \quad \text{and} \quad \langle U_P \psi | U_P \phi \rangle = \langle \psi | \phi \rangle$$

---

## 3. Input & Output Contracts

### 3.1 Input Contract
Consumes ONLY a validated `QTMIRModel` from `src/module3/qtm_ir/`. The engine does **NOT** require `RUTM_IR`, `UTMProgram`, or `RUTMConfiguration`. Validation via `validate_qtm_ir(model)` is strictly enforced prior to execution.

### 3.2 Output Contract (`QTMExecutionTrace`)
Execution returns `QTMExecutionTrace` containing:
- `states`: List of `QTMIRStateVector` $[|\psi(0)\rangle, |\psi(1)\rangle, \dots, |\psi(T)\rangle]$
- `step_count`: Total evolution steps $T$
- `initial_state`: $|\psi(0)\rangle$
- `final_state`: $|\psi(T)\rangle$
- `norm_trace`: List of floats $[||\psi(0)||, \dots, ||\psi(T)||]$
- `halted`: Boolean indicating if final state basis is halted

---

## 4. Execution Engine Functions & API

### 4.1 Forward Unitary Evolution (`apply_unitary`)
`apply_unitary(model, state)` applies $U_P$ using the sparse `forward_mapping`.

### 4.2 Adjoint Evolution (`apply_adjoint`)
`apply_adjoint(model, state)` applies $U_P^\dagger$ using the validated `reverse_mapping` $R_P^{-1}$. Satisfies round-trip identities:
$$U_P^\dagger U_P |\psi\rangle = |\psi\rangle \quad \text{and} \quad U_P U_P^\dagger |\psi\rangle = |\psi\rangle$$

### 4.3 Matrix Cross-Validation (`apply_matrix` & `execute_matrix`)
Optional verification path multiplying dense matrix $[U_P]_{N \times N}$ against input state vector column. Verified to agree with mapping-based execution.

### 4.4 Multi-Step Execution (`execute`)
`execute(model, initial_state, steps)` computes the evolution trace for $N$ steps.

### 4.5 Utility Functions (`inner_product` & `normalize_state`)
- `inner_product(v1, v2)`: Computes $\langle v_1 | v_2 \rangle = \sum_b \alpha_b^* \beta_b$.
- `normalize_state(state)`: Explicit utility dividing state vector by $\|\psi\|$. (Note: `apply_unitary` naturally preserves norm and does **NOT** auto-renormalize).

---

## 5. Fixed Point Semantics

- **Halting Fixed Point:** If $R_P(C_\text{halt}) = C_\text{halt}$, then $U_P |C_\text{halt}\rangle = |C_\text{halt}\rangle$.
- **Error Fixed Point:** If $R_P(C_\text{error}) = C_\text{error}$, then $U_P |C_\text{error}\rangle = |C_\text{error}\rangle$.
Both remain unitary fixed points with zero measurement or state collapse.

---

## 6. Error & Validation Rejection Policies

- **Invalid Model Rejection:** Fails with `QTMExecutionError` if `validate_qtm_ir(model)` returns `valid=False`.
- **Unknown Basis ID Rejection:** Fails with `QTMExecutionError` if state vector contains a basis ID missing from `model.basis_states`.
- **Missing Transition Rejection:** Fails with `QTMExecutionError` if `model.transition_mapping` lacks a transition for an active basis state.

---

## 7. Verification & Test Summary

- **Module 3 Stage 7 Unit Tests:** 18 / 18 PASS ([`tests/module3/test_stage7_qtm_execution.py`](../../tests/module3/test_stage7_qtm_execution.py))
- **Module 3 Total Unit Tests:** 94 / 94 PASS (16 Stage 2 + 15 Stage 3 + 10 Stage 4 + 14 Stage 5 + 21 Stage 6 + 18 Stage 7)
- **Module 1 Regression:** 79 / 79 PASS
- **Module 2 Regression:** 155 / 155 PASS
- **Production Files:**
  - [`src/module3/execution/__init__.py`](../../src/module3/execution/__init__.py)
  - [`src/module3/execution/engine.py`](../../src/module3/execution/engine.py)
  - [`src/module3/__init__.py`](../../src/module3/__init__.py)
  - [`docs/module-3/STAGE_7_QTM_EXECUTION_ENGINE.md`](STAGE_7_QTM_EXECUTION_ENGINE.md)
