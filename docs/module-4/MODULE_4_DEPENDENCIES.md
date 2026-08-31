# Module 4 Dependencies & Architectural Boundaries

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN DEPENDENCIES  

---

## 1. Upstream Module Dependencies

Module 4 depends on frozen upstream contracts:

- **Module 3 QTM-IR:** `src/module3/qtm_ir/model.py` (`QTMIRModel`, `QTMIRBasisState`, `QTMIRStateVector`, `QTMIRTransitionMapping`, `QTMIRMatrixRepresentation`, `QTMIRProvenance`).
- **Module 3 Validator:** `src/module3/qtm_ir/validator.py` (`validate_qtm_ir()`).
- **Module 3 Execution & Equivalence:** `src/module3/execution/` and `src/module3/equivalence/`.

---

## 2. Inviolable Dependency & Boundary Rules

1. **Frozen Upstream Policy:** Module 4 MUST NOT alter, weaken, patch, or retrofit any code, specification, or test suite in Module 1, Module 2, or Module 3. Module 3 is completely frozen.
2. **Zero Ingest Mutation:** Ingested `QTMIRModel` instances are strictly read-only.
3. **No Mandatory External SDKs:** External third-party SDKs (Qiskit, Cirq, etc.) MUST NOT become mandatory runtime dependencies for Module 4 core synthesis.
4. **Module 5 Isolation:** Downstream Module 5 (hardware transpilation) MUST NOT be invoked or implemented within Module 4.
