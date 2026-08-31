# Module 4 Scope & Formal Classification Document

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN SCOPE  

---

## 1. Constitutional Classifications

Every architectural responsibility of Module 4 is explicitly classified into one of five strict categories:

### 1.1 `CONFIRMED`
- **QTM-IR Ingestion:** Ingesting validated `QTMIRModel` from frozen Module 3.
- **Finite Configuration Domain Contract:** Requiring explicit specification of finite domain $D_\text{fin} \subset \mathcal{C}_R$ closed under $R_P$ and $R_P^{-1}$.
- **Injective Configuration Encoding:** Enforcing $E : D_\text{fin} \to \{0,1\}^n$ such that $C_1 \neq C_2 \implies E(C_1) \neq E(C_2)$.
- **Logical History Preservation:** Encoding classical history $H$ into registers when non-empty.
- **Canonical Primitive Gate Set:** Establishing $\text{Toffoli} + \text{CNOT} + \text{X}$ as the canonical logical reversible gate set.
- **Clean Ancilla Uncomputation:** Guaranteeing all physical workspace ancillas return to $|0\rangle$.
- **3-Level Equivalence Verification Policy:** Symbolic exact basis matching, numerical state vector norm $\epsilon < 10^{-12}$, and matrix operator norm $\epsilon < 10^{-12}$.
- **Complete Provenance Chain:** Preserving $\text{RUTM} \to \text{RUTM-IR} \to \text{QTM-IR} \to \text{Circuit-IR}$.
- **100% Deterministic Synthesis:** Reproducible circuit output for identical inputs.

### 1.2 `PROVISIONAL`
- **`QuantumCircuitIR` AST Data Model:** Formal dataclasses/schemas for registers, gates, and metadata.
- **Bitstring Allocation Layout:** Exact bit allocation for state, tape, head, and history registers.
- **Gate Decomposition Templates:** Multi-controlled Toffoli decomposition patterns into 1-qubit/2-qubit gates.

### 1.3 `DEFERRED`
- **Circuit Depth & Width Optimization:** Automated gate cancellation, commuting gate reordering, and register reuse algorithms.
- **Multi-Target Gate Set Translation:** Compiling to distinct universal quantum gate sets (e.g., Clifford+T).

### 1.4 `FORBIDDEN`
- **Hardware Physical Transpilation:** Physical qubit mapping, coupling graph routing, swap insertion (reserved for Module 5).
- **Pulse-Level Control:** Microwave pulse generation or hardware device calibration.
- **Modifying Upstream Modules:** Mutating code, tests, or docs in Module 1, Module 2, or Module 3.
- **Redefining QTM Semantics:** Altering or weakening $U_P \circ \iota = \iota \circ R_P$.

### 1.5 `UNRESOLVED`
- **None.** All preliminary architectural questions resolved during Scope Review and Micro Closure.
