# Stage 3 Specification — Reversible Gate Realization & QTM Transition Realization

**Module:** Module 4 — Quantum Circuit Synthesis  
**Stage:** Stage 3 — Reversible Gate Realization & QTM Transition Realization  
**Status:** FORMALLY CLOSED / FROZEN  

---

## 1. Primary Objective & Semantic Contract

Stage 3 implements the first executable logical reversible synthesis layer in Module 4. It synthesizes a backend-independent `QuantumCircuitIR` model that unitarily realizes the QTM transition operator $R_P$ on a finite configuration domain $D_\text{fin}$:

$$U_C |E(C)\rangle = |E(R_P(C))\rangle \quad \forall C \in D_\text{fin}$$

---

## 2. Input & Output Contracts

### Upstream Input Contracts
- `QTMIRModel` (Module 3)
- `FiniteDomainContract` ($D_\text{fin} \subset \mathcal{C}_R$, $|D_\text{fin}| < \infty$, $R_P(D_\text{fin}) \subseteq D_\text{fin}$, $R_P^{-1}(D_\text{fin}) \subseteq D_\text{fin}$)
- `RegisterEncodingSpec` ($E : D_\text{fin} \to \{0,1\}^n$)
- State and symbol encoding mappings

### Primary Output Contract
- Validated `QuantumCircuitIR` containing:
  - Logical qubit registers (`STATE`, `TAPE`, `HEAD`, `HISTORY`, `STEP`, `STATUS`, `ANCILLA`).
  - Primitive logical gate operations ($\text{X}$, $\text{CNOT}$, $\text{TOFFOLI}$).
  - Workspace ancilla declarations with clean $|0\rangle$ status.
  - Stage 3 provenance metadata.

---

## 3. Transition Table Construction & Bijectivity Validation

The synthesis engine constructs the finite transition table:
$$T = \{ E(C) \longrightarrow E(R_P(C)) \mid C \in D_\text{fin} \}$$

### Invariants
1. **Totality:** $\text{dom}(T) \equiv E(D_\text{fin})$.
2. **Bijectivity:** $T$ is strictly injective and surjective on $E(D_\text{fin})$.
3. **Fixed-Point Preservation:** Halted configurations ($C_\text{halt}$) and error configurations ($C_\text{error}$) transition to their exact Module 2 semantics ($U_C |E(C_\text{halt})\rangle = |E(C_\text{halt})\rangle$).

---

## 4. Reversible Boolean Synthesis Strategy

For each pair $x = E(C) \mapsto y = E(R_P(C))$ in $T$:
1. Identifies bit positions $i$ where $x[i] \neq y[i]$.
2. Synthesizes a multi-controlled NOT transformation controlled on all other state bits matching $x$.
3. Employs **Bennett Uncomputation Protocol** for control count $k > 2$:
   - **Compute:** Build Toffoli AND-tree using workspace ancillas ($a_0, a_1, \dots$).
   - **Apply:** Target $X$, $\text{CNOT}$, or $\text{TOFFOLI}$ gate using root ancilla.
   - **Uncompute:** Reverse Toffoli AND-tree in exact opposite order, restoring all workspace ancillas to $|0\rangle$.

---

## 5. Frozen Primitive Gate Semantics

The circuit contains ONLY frozen logical primitive gates:
- **Pauli-X ($X$):** $x \mapsto x \oplus 1$ (Arity 1).
- **CNOT ($\text{CNOT}$):** $(c, t) \mapsto (c, t \oplus c)$ (Arity 2).
- **Toffoli ($\text{TOFFOLI}$):** $(c_1, c_2, t) \mapsto (c_1, c_2, t \oplus (c_1 \land c_2))$ (Arity 3).

---

## 6. Ancilla Discipline & Bennett Uncomputation

- Workspace ancillas are initialized to $|0\rangle$ (`CLEAN`).
- Bennett uncomputation guarantees that every workspace ancilla returns to $|0\rangle$ at circuit termination (`expected_final_status = CLEAN`).
- Logical history $H$ is preserved as a data register and is NEVER converted to workspace ancilla.

---

## 7. Independent 4-Level Verification Engine (`verify_transition_realization`)

The Stage 3 verifier independently computes every verification level without proxy inheritance:

### LEVEL 1: Exact Symbolic Computational-Basis Verification
- Verifies $U_C |E(C)\rangle = |E(R_P(C))\rangle$ for all $C \in D_\text{fin}$ using exact bitstring identity.
- Output field: `symbolic_basis_pass` (boolean).

### REVERSE EXECUTION VERIFICATION
- Verifies $U_C^\dagger |E(R_P(C))\rangle = |E(C)\rangle$ for all $C \in D_\text{fin}$ using reverse gate sequence execution.
- Output field: `reverse_execution_pass` (boolean).

### LEVEL 2: Numerical State-Vector & Superposition Verification
- Constructs deterministic normalized quantum state vector $|\psi\rangle = \sum_C \alpha_C |E(C)\rangle$ with non-zero complex amplitudes $\alpha_C \in \mathbb{C}$.
- Verifies L2 norm difference $\|\psi_\text{actual} - \psi_\text{expected}\|_2 < 10^{-12}$.
- Verifies norm preservation $\|U_C \psi\|_2 = \|\psi\|_2 < 10^{-12}$.
- Output field: `superposition_pass` (boolean), residual stored in `superposition_residual`.

### LEVEL 3: Numerical Operator Unitarity & Correspondence Verification
- Evaluates complete composed circuit operator $U_C = U_{G_{m-1}} \dots U_{G_0}$.
- Verifies Left Unitarity $\|U_C^\dagger U_C - I\|_2 < 10^{-12}$.
- Verifies Right Unitarity $\|U_C U_C^\dagger - I\|_2 < 10^{-12}$.
- Verifies Matrix/Transition Semantic Correspondence $U_C |E(C)\rangle = |E(R_P(C))\rangle$.
- Output field: `operator_unitary_pass` (boolean), residuals stored in `left_unitarity_residual` and `right_unitarity_residual`.

---

## 8. Determinism & Provenance

- **100% Deterministic Synthesis:** Identical inputs yield byte-for-byte identical `QuantumCircuitIR` outputs.
- **Provenance Link:** Preserves $\text{RUTM} \to \text{RUTM-IR} \to \text{QTM-IR} \to \text{Circuit-IR}$ with `synthesis_method = "STAGE_3_LOGICAL_REVERSIBLE_SYNTHESIS"`.
