# Module 4 Interface Specification — Upstream & Downstream Contracts

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN INTERFACES  

---

## 1. Upstream Interface: Module 3 $\to$ Module 4

Module 4 ingests validated QTM-IR instances from Module 3.

### Read-Only Upstream Dependencies
- `QTMIRModel` (`src/module3/qtm_ir/model.py`)
- `QTMIRBasisState`
- `QTMIRStateVector`
- `QTMIRTransitionMapping`
- `validate_qtm_ir()` (`src/module3/qtm_ir/validator.py`)

### Invariant Contract
All ingested QTM-IR models satisfy $U_P^\dagger U_P = I$ and $U_P \circ \iota = \iota \circ R_P$. Module 3 is read-only and immutable.

---

## 2. Downstream Interface: Module 4 $\to$ Module 5

Module 4 produces a structured `QuantumCircuitIR` for target architecture / hardware mapping in Module 5.

### Provisional Output Data Model (`QuantumCircuitIR`)
- `circuit_id`: Unique identifier string.
- `qubit_registers`: Dict of named register declarations (State, Tape, Head, History, Ancilla).
- `gates`: Ordered list of logical gate operations ($\text{Toffoli}, \text{CNOT}, \text{X}$).
- `domain_contract`: Embedded `FiniteDomainContract`.
- `encoding_spec`: Embedded `RegisterEncodingSpec`.
- `provenance`: Full compiler provenance trace.
- `metrics`: Circuit depth, width, total gate count, ancilla count.

### Boundary Firewall
Hardware transpilation, coupling graph routing, swap insertion, and pulse generation are **FORBIDDEN** in Module 4 and reserved exclusively for Module 5.
