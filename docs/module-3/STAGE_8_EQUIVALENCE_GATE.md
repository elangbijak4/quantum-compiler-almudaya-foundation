# Stage 8 Specification & Architecture — Reversible $\to$ Quantum Equivalence Verification Gate

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 8 — Reversible $\to$ Quantum Equivalence Verification Gate  
**Status:** FORMALLY CLOSED / FROZEN  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md), [`STAGE_2_QTM_STATE_MODEL.md`](STAGE_2_QTM_STATE_MODEL.md), [`STAGE_3_QTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_QTM_OPERATIONAL_SEMANTICS.md), [`STAGE_4_UNITARY_EQUIVALENCE_PROOF.md`](STAGE_4_UNITARY_EQUIVALENCE_PROOF.md), [`STAGE_5_QTM_IR_MODEL_AND_VALIDATOR.md`](STAGE_5_QTM_IR_MODEL_AND_VALIDATOR.md), [`STAGE_6_RUTM_TO_QTM_TRANSLATOR.md`](STAGE_6_RUTM_TO_QTM_TRANSLATOR.md), [`STAGE_7_QTM_EXECUTION_ENGINE.md`](STAGE_7_QTM_EXECUTION_ENGINE.md)  

---

## 1. Stage 8 Purpose & Architectural Role

Stage 8 implements the independent **Reversible $\to$ Quantum Equivalence Verification Gate**. Its purpose is to independently execute both Module 2 reversible path $R_P$ and Module 3 QTM quantum path $U_P$, verifying exact step-by-step semantic correspondence for every step $t \in \{0, 1, \dots, T\}$ within a declared finite verification horizon $T$.

```
 Path A (Reversible)         Path B (Quantum)
       C_0                        |C_0> = ι(C_0)
        |                           |
   R_P  v                      U_P  v
       C_1 ----- Equivalence? ----> |ψ_1>  (= ι(C_1))
        |                           |
   R_P  v                      U_P  v
       ...                         ...
        |                           |
   R_P  v                      U_P  v
       C_T ----- Equivalence? ----> |ψ_T>  (= ι(C_T))
```

> [!IMPORTANT]
> **Stage 8 Independence Boundary:**  
> The gate MUST NOT derive classical states from quantum states or vice versa (except via the canonical embedding $\iota(C)$).
> - Path A is driven independently by Module 2 `forward_step_rutm()`.
> - Path B is driven independently by Module 3 Stage 7 `apply_unitary()`.

---

## 2. Mathematical Foundation & Commuting Diagram

The iterated commuting relation verified by Stage 8 is:
$$U_P^t \circ \iota = \iota \circ R_P^t \quad \forall t \in \{0, 1, \dots, T\}$$

represented by the commutative diagram:

$$\begin{array}{ccc}
C_0 & \xrightarrow{R_P^t} & C_t \\
\iota \downarrow & & \downarrow \iota \\
|C_0\rangle & \xrightarrow{U_P^t} & |\psi_t\rangle = |C_t\rangle
\end{array}$$

### Mathematical Claim vs. Executable Evidence
- **Mathematical Theorem:** Proof established in Stage 4 ($U_P \circ \iota = \iota \circ R_P$).
- **Executable Evidence:** Stage 8 provides empirical runtime verification that the implemented Module 2 and Module 3 software artifacts satisfy the theorem over horizon $T$.

---

## 3. Three-Valued Verification Gate Outcomes

Stage 8 returns `EquivalenceResult` with exactly three top-level outcomes:

1. **`PASS`**: Both paths executable, all inputs valid, and every verified step $t \in \{0, \dots, T\}$ satisfies $|\psi_t\rangle = \iota(C_t)$ with zero divergence.
2. **`FAIL`**: Both paths executable, but semantic divergence observed (support mismatch, amplitude mismatch, missing basis state, extra amplitude, or history identity mismatch).
3. **`INCONCLUSIVE`**: Verification could not legitimately complete (invalid horizon $T < 0$, QTM-IR validation failure `valid=False`, domain truncation where $C_t \notin D_\text{QTM}$, or unsupported program fixture).

---

## 4. Input & Output Contracts

### 4.1 Input Contract
- `rutm_program`: `Union[RUTM_IR, UTMProgram]`
- `qtm_ir`: `QTMIRModel` (validated via `validate_qtm_ir()`)
- `initial_config`: Optional `RUTMConfiguration` $C_0$
- `max_steps`: Verification horizon $T \ge 0$
- `verify_reverse`: Optional boolean requesting reverse adjoint equivalence check ($U_P^\dagger \iota(C_t) = \iota(R_P^{-1}(C_t))$)

### 4.2 Output Contract (`EquivalenceResult` & `EquivalenceStepResult`)
- `status`: `EquivalenceStatus` (`PASS` / `FAIL` / `INCONCLUSIVE`)
- `max_steps`: $T$
- `verified_steps`: Number of steps verified ($k \le T + 1$)
- `first_failure_step`: Index $k$ of first divergence if FAIL/INCONCLUSIVE, else `None`
- `trace`: List of `EquivalenceStepResult` records
- `diagnostics`: List of failure/warning diagnostic messages
- `provenance`: `QTMIRProvenance`

---

## 5. Invariants & False-Positive Protections

- **Every-Step Verification:** Every step $t = 0 \dots T$ is inspected (final-state-only comparison is forbidden).
- **Exact Support & Amplitude Matching:** Support size MUST equal 1 ($\{|\iota(C_t)|\}$), amplitude MUST equal $1.0 + 0i$.
- **History Identity Preservation:** Configuration identity includes history $H$. Mismatched history causes `FAIL`.
- **Halting & Error Fixed Points:** $R_P(C_\text{fixed}) = C_\text{fixed} \iff U_P |C_\text{fixed}\rangle = |C_\text{fixed}\rangle$.
- **Independent Witness:** Re-verifies canonical basis IDs directly from configuration fields to prevent shared bugs.

---

## 6. Verification & Test Summary

- **Module 3 Stage 8 Unit Tests:** 17 / 17 PASS ([`tests/module3/test_stage8_equivalence_gate.py`](../../tests/module3/test_stage8_equivalence_gate.py))
- **Module 3 Total Unit Tests:** 111 / 111 PASS (16 Stage 2 + 15 Stage 3 + 10 Stage 4 + 14 Stage 5 + 21 Stage 6 + 18 Stage 7 + 17 Stage 8)
- **Module 1 Regression:** 79 / 79 PASS
- **Module 2 Regression:** 155 / 155 PASS
- **Production Files:**
  - [`src/module3/equivalence/__init__.py`](../../src/module3/equivalence/__init__.py)
  - [`src/module3/equivalence/result.py`](../../src/module3/equivalence/result.py)
  - [`src/module3/equivalence/gate.py`](../../src/module3/equivalence/gate.py)
  - [`src/module3/__init__.py`](../../src/module3/__init__.py)
  - [`docs/module-3/STAGE_8_EQUIVALENCE_GATE.md`](STAGE_8_EQUIVALENCE_GATE.md)
