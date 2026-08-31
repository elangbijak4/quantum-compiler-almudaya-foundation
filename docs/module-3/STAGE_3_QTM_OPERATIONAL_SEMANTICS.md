# Stage 3 Specification & Architecture — QTM Operational Semantics & Unitary Operator Formulation

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 3 — QTM Operational Semantics & Unitary Operator Formulation  
**Status:** CLOSURE REVIEW COMPLETE / FROZEN  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md), [`STAGE_2_QTM_STATE_MODEL.md`](STAGE_2_QTM_STATE_MODEL.md)  

---

## 1. Executive Summary & Lifting Principle

Module 3 Stage 3 implements the central operational quantum semantics of the compiler pipeline, lifting the discrete classical reversible configuration transition $R_P : \mathcal{C}_R \to \mathcal{C}_R$ established in Module 2 into a permutation-style unitary operator $U_P : \mathcal{H}_Q \to \mathcal{H}_Q$ over computational basis Hilbert space $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$:

$$\mathcal{C}_R \xrightarrow{\quad R_P \quad} \mathcal{C}_R \quad \implies \quad U_P |C_R\rangle = |R_P(C_R)\rangle = (\iota \circ R_P)(C_R)$$

> [!IMPORTANT]
> **Central Semantic Lifting Claim:**  
> Module 3 lifts reversible classical transitions $R_P$ into a permutation-style unitary operator $U_P$ over the Hilbert space whose computational basis is indexed by reversible configurations.  
> It does **NOT** claim to generate arbitrary quantum gate dynamics (such as Hadamard or arbitrary phase rotations), which are synthesized in Module 4.

---

## 2. Central Equations & Invariants

### 1. Basis-State Forward Evolution
$$U_P |C_R\rangle = |R_P(C_R)\rangle \quad \forall C_R \in \mathcal{C}_R$$

### 2. Outer-Product Operator Formulation
$$U_P = \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle C|$$

### 3. Linear Extension Over Superpositions
$$U_P \left( \sum_{C \in \mathcal{C}_R} \alpha_C |C_R\rangle \right) = \sum_{C \in \mathcal{C}_R} \alpha_C |R_P(C_R)\rangle \quad (\alpha_C \in \mathbb{C})$$

### 4. Adjoint / Inverse Operational Evolution
$$U_P^\dagger |R_P(C_R)\rangle = |C_R\rangle \quad \implies \quad U_P^\dagger = \sum_{C' \in \mathcal{C}_R} |R_P^{-1}(C')\rangle \langle C'|$$

### 5. Unitarity Invariant
If $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection, then:
$$U_P^\dagger U_P = U_P U_P^\dagger = I_{\mathcal{H}_Q}$$

### 6. Forward Commuting Correspondence Theorem
$$\mathbf{U_P \circ \iota = \iota \circ R_P}$$

```
        R_P
  C_R --------> C_R'
   |             |
   | ι           | ι
   ▼             ▼
  |C_R⟩ --U_P-> |C_R'⟩
```

### 7. Inverse Adjoint Commuting Correspondence Theorem
$$\mathbf{U_P^\dagger \circ \iota = \iota \circ R_P^{-1}}$$

---

## 3. Forward & Reverse Round-Trip Invariants

For any basis vector $|C_R\rangle$ or superposition state vector $|\psi\rangle \in \mathcal{H}_Q$:

$$U_P^\dagger (U_P |\psi\rangle) = |\psi\rangle \quad \text{and} \quad U_P (U_P^\dagger |\psi\rangle) = |\psi\rangle$$

> [!NOTE]
> **Adjoint Terminology:** $U_P^\dagger$ describes mathematical **inverse computational evolution** (or **adjoint operational evolution**). It does **NOT** establish physical hardware or thermodynamic time-reversal.

---

## 4. Norm & Inner-Product Preservation

### Theorem 4.1 (Norm Preservation)
For all state vectors $|\psi\rangle \in \mathcal{H}_Q$:
$$\| U_P |\psi\rangle \| = \| |\psi\rangle \|$$
If $|\psi\rangle \in \mathcal{S}_Q$ (unit norm), then $U_P |\psi\rangle \in \mathcal{S}_Q$.

### Theorem 4.2 (Inner-Product Preservation)
For all state vectors $|\psi\rangle, |\phi\rangle \in \mathcal{H}_Q$:
$$\langle U_P \psi | U_P \phi \rangle = \langle \psi | \phi \rangle$$

---

## 5. Total Bijectivity Validation & Collision Safety

To guarantee $U_P^\dagger U_P = I$, the classical transition $R_P$ MUST be a total bijection:
1. **Domain Closure:** $R_P(\mathcal{C}_{R,\text{fin}}) \subseteq \mathcal{C}_{R,\text{fin}}$.
2. **Injectivity:** $C_1 \neq C_2 \implies R_P(C_1) \neq R_P(C_2)$ (no collisions).
3. **Surjectivity:** Every element in the domain is reachable under $R_P$.

If a non-bijective transition mapping is supplied (such as $R_P(C_1) = R_P(C_2) = C_{\text{target}}$ for $C_1 \neq C_2$), construction or verification fails with a `ValueError` or returns `is_bijective = False`.

---

## 6. Formal-Executable Audit & Consistency Clarifications

### A. Executable Unitarity Verification vs. Abstract Mathematical Theorem
Executable unitarity verification on finite transition-closed domains (`verify_unitarity()`) establishes the unitary property through bijective transition semantics, inverse round-trip consistency, and state-vector norm preservation. The abstract equality $U_P^\dagger U_P = I$ over $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$ remains the normative mathematical statement; the executable software does not numerically materialize an infinite-dimensional identity matrix.

### B. Finite Matrix Representation ($[U_P]$) vs. Abstract Operator ($U_P$)
The architecture strictly distinguishes:
- **Abstract Operator $U_P$:** Operating on $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$ (potentially infinite-dimensional).
- **Finite Permutation Matrix $[U_P]$:** $N \times N$ matrix representation over an ordered finite transition-closed basis domain $[b_0, b_1, \dots, b_{N-1}]$.

`PermutationMatrixRepresentation.is_unitary()` explicitly computes and verifies both left-unitarity ($[U_P]^\dagger [U_P] = I_{N \times N}$) and right-unitarity ($[U_P] [U_P]^\dagger = I_{N \times N}$).

### C. Finite Verification Mappings & Complementary Domain Identity Extension
When constructing an operator from a finite mapping $M : D \to D$ (`create_unitary_operator_from_mapping`), the mapping MUST be transition-closed ($D = M(D)$) and bijective over $D$. For configurations outside $D$, the operator performs an explicit identity extension ($R_P(C) = C$ for $C \in \mathcal{C}_R \setminus D$), ensuring total global bijectivity across all of $\mathcal{C}_R$. A finite-domain mapping $D \to D$ induces a unitary finite restriction $[U_P]$ on $\mathcal{H}_D = \text{span}\{|C\rangle \mid C \in D\}$, while global unitarity relies on total identity extension.

---

## 7. Public API Reference

| Class / Function | Signature / Type | Description & Operational Contract |
| :--- | :--- | :--- |
| `LiftedUnitaryOperator` | `class` | Lifted unitary operator $U_P = \sum |R_P(C)\rangle \langle C|$. Provides `apply_basis()`, `apply_basis_adjoint()`, `apply_state()`, `apply_state_adjoint()`, `verify_bijectivity()`, `verify_unitarity()`. |
| `PermutationMatrixRepresentation` | `class` | Finite $N \times N$ matrix representation $[U_P]$. Provides `is_permutation()` and `is_unitary()` (verifying $[U_P]^\dagger [U_P] = I$ and $[U_P] [U_P]^\dagger = I$). |
| `create_unitary_operator_from_program` | `UTMProgram -> LiftedUnitaryOperator` | Factory constructing $U_P$ from Module 1 `UTMProgram` using Module 2 forward/reverse RUTM step semantics. |
| `create_unitary_operator_from_mapping` | `Dict[QuantumBasisState, QuantumBasisState] -> LiftedUnitaryOperator` | Factory constructing $U_P$ from an explicit finite bijective basis state mapping. Rejects non-bijective collisions. |

---

## 8. Implementation Non-Goals

Stage 3 strictly excludes:
- Quantum circuit gate synthesis (Toffoli, CNOT, Hadamard, Pauli-X).
- Qubit register layouts, bitstrings, or physical qubit mapping.
- Transpilation, Qiskit/Cirq export, or quantum hardware execution.

---

## 9. Verification & Regression Status

- **Module 3 Stage 3 Unit Tests:** 15 / 15 PASS (`tests/module3/test_stage3_unitary_operator.py`)
- **Module 3 Total Unit Tests:** 31 / 31 PASS (16 Stage 2 + 15 Stage 3)
- **Module 1 Regression:** 79 / 79 PASS
- **Module 2 Regression:** 155 / 155 PASS
- **Production Files Created:**
  - [`src/module3/qtm/operator.py`](../../src/module3/qtm/operator.py)
  - [`tests/module3/test_stage3_unitary_operator.py`](../../tests/module3/test_stage3_unitary_operator.py)
- **Production Files Modified:**
  - [`src/module3/qtm/__init__.py`](../../src/module3/qtm/__init__.py)
  - [`src/module3/__init__.py`](../../src/module3/__init__.py)
