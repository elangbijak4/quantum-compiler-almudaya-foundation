# Module 3 Dependencies Specification

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Status:** ARCHITECTURAL REVIEW COMPLETE / READY FOR STAGE 1  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md)  

---

## 1. Upstream Internal Dependencies

1. **Module 1 (FROZEN):**
   - [`src/module1/utm/model.py`](../../src/module1/utm/model.py): `UTMProgram`, `UTMConfiguration`, `Direction`, `TransitionAction`.
2. **Module 2 (FROZEN):**
   - [`src/module2/rutm/model.py`](../../src/module2/rutm/model.py): `RUTMConfiguration`, `RUTMHistoryPolicy`.
   - [`src/module2/rutm_ir/model.py`](../../src/module2/rutm_ir/model.py): `RUTM_IR`, `validate_rutm_ir()`.
   - [`src/module2/execution/executor.py`](../../src/module2/execution/executor.py): `execute_rutm_ir()`, `RUTMExecutionResult`.
   - [`src/module2/verification/equivalence.py`](../../src/module2/verification/equivalence.py): `verify_utm_to_rutm_equivalence()`.

---

## 2. External Tooling & Standard Library Dependencies

- **Python Standard Library:** `dataclasses`, `typing`, `json`, `unittest`, `math`, `ast`, `os`, `sys`, `io`.
- **Numerical Computation (Optional / Standard):** `numpy` (for matrix representation / unitary verification if authorized).

---

## 3. Forbidden Dependencies

- **No Modifications to Frozen Modules:** Module 3 must NOT modify `src/module1/`, `src/module2/`, `tests/module1/`, `tests/module2/`, `docs/module-1/`, `docs/module-2/`.
- **No Direct Circuit Synthesis in Module 3:** Circuit gate synthesis (Toffoli / CNOT / X) and hardware backend transpilation belong strictly to Module 4.
- **No Duplicate Root Constitution:** Creation of a second `main-technical-refference.md` is strictly forbidden.
