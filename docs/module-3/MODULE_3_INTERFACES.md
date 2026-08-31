# Module 3 Interface Specifications

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Status:** ARCHITECTURAL REVIEW COMPLETE / READY FOR STAGE 1  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md)  

---

## 1. Upstream Interface: Module 2 $\to$ Module 3 Ingestion Contract

### Ingested Objects:
- **`RUTM_IR`:** Ingested from `src.module2.rutm_ir.model.RUTM_IR`. Defines state set $\mathcal{Q}$, alphabets $\Sigma, \Gamma$, blank $B$, initial/halt states, transition rules $\delta_R$, history policy $\text{HistoryPolicy}_R$, provenance metadata.
- **`RUTMConfiguration`:** Ingested from `src.module2.rutm.model.RUTMConfiguration`. Represents discrete classical state $C_R = (q, T, h, H, k, \text{halted}, \text{error})$.
- **`RUTMExecutionResult`:** Ingested from `src.module2.execution.result.RUTMExecutionResult`. Provides execution traces $[C_{R,0}, C_{R,1}, \dots, C_{R,n}]$.

### Invariant Contract:
Module 3 assumes `validate_rutm_ir()` has returned `valid = True` and that trace reversibility has been verified by `verify_trace_reversibility()`.

---

## 2. Module 3 Exported Output Contract: Module 3 $\to$ Module 4 (Quantum Circuit Layer)

### Exported Artifacts:
- **`QTM-IR` Representation:** Exportable quantum machine specification encapsulating Hilbert space basis state definitions $\mathcal{H}_Q$, state vectors $|\psi\rangle$, and unitary transition operators $U_P$.
- **Unitary Operator Specification ($U_P$):** Permutation unitary operator $U_P = \sum |R_P(C)\rangle \langle C|$ satisfying $U_P^\dagger U_P = I$.
- **Uncomputation Obligation Protocol:** Formal specification of history stack uncomputation obligations ($U_P^\dagger |C_{\text{final}}\rangle = |C_0\rangle$) for gate-level ancilla cleanup in Module 4.

---

## 3. Boundary Exclusions (Not Owned by Module 3)

- **Quantum Circuit Gate Synthesis:** Toffoli, CNOT, and Pauli-X gate decompositions belong strictly to Module 4.
- **Qubit Register Allocation & Topology:** Physical qubit layout, register truncation, and transpilation belong strictly to Module 4.
