# Stage 2 Specification & Architecture — QTM State Model & Hilbert Space Representation

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 2 — QTM State Model & Hilbert Space Representation  
**Status:** STAGE 2 MICRO CLOSURE PATCH COMPLETE / FROZEN READY  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md)  

---

## 1. Executive Summary

Module 3 Stage 2 implements the software state model corresponding to the Stage 1 mathematical abstraction:

$$\mathcal{C}_R \xrightarrow{\quad \iota \quad} |C_R\rangle \in \mathcal{H}_Q = \ell^2(\mathcal{C}_R) \implies |\psi\rangle = \sum_{C \in \mathcal{C}_R} \alpha_C |C_R\rangle \quad (\alpha_C \in \mathbb{C})$$

Stage 2 provides the executable substrate for quantum computational basis states, sparse state vectors, complex inner products $\langle \psi | \phi \rangle$, state vector arithmetic, norm calculations $\| |\psi\rangle \|$, and normalized quantum state verification ($\mathcal{S}_Q$).

---

## 2. Mathematical vs Executable Representation Model

> [!IMPORTANT]
> **Representation Principle:**  
> The abstract Hilbert space $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$ is countably infinite-dimensional because the RUTM tape $T : \mathbb{Z} \to \Gamma$ is unbounded.  
> The Stage 2 implementation provides a **finite executable sparse representation model** (`QTMStateVector`). It does NOT materialize an infinite-dimensional space or a dense finite matrix.

```
Abstract Hilbert Space:  H_Q = l^2(C_R)    (Infinite-dimensional)
                                |
Executable Representation: QTMStateVector   (Sparse Dict[QuantumBasisState, complex])
```

---

## 3. Computational Basis State Model ($|C_R\rangle$)

The computational basis state $|C_R\rangle$ encapsulates a valid `RUTMConfiguration` $C_R = (q, T, h, H, k, \text{halted}, \text{error})$ from Module 2 Stage 2.

### Basis Identity & Orthogonality
- **Semantic Configuration Identity:** Basis states compare equal (`__eq__`) and hash identically (`__hash__`) based on the canonical value tuple of the underlying `RUTMConfiguration`:
  $$\text{Key}(C_R) = (q, \text{sorted}(T \setminus \{'\_'\}), h, H, k, \text{halted}, \text{error})$$
- **Dirac Inner Product Orthogonality:**
  $$\langle C_1 | C_2 \rangle = \delta_{C_1, C_2} = \begin{cases} 1.0 + 0.0j & \text{if } C_1 = C_2 \\ 0.0 + 0.0j & \text{if } C_1 \neq C_2 \end{cases}$$

---

## 4. Sparse Quantum State Vector Model (`QTMStateVector`)

A quantum state vector $|\psi\rangle = \sum_{C \in \mathcal{C}_R} \alpha_C |C_R\rangle$ is represented as a sparse mapping from `QuantumBasisState` to complex amplitude $\alpha_C \in \mathbb{C}$.

### Key Properties & Operations
1. **Complex Amplitudes:** Supports arbitrary complex numbers ($\alpha_C \in \mathbb{C}$) including phase representations (e.g. $1/\sqrt{2}$, $i/\sqrt{2}$).
2. **Inner Product $\langle \psi | \phi \rangle$:**
   $$\langle \psi | \phi \rangle = \sum_{C \in \text{basis}(\psi) \cap \text{basis}(\phi)} \alpha_C^* \beta_C$$
   Computes complex conjugation $\alpha_C^*$ on the left state vector strictly according to linear algebra.
3. **Vector Norm $\| |\psi\rangle \|$:**
   $$\| |\psi\rangle \| = \sqrt{\langle \psi | \psi \rangle} = \sqrt{\sum_{C \in \mathcal{C}_R} |\alpha_C|^2}$$
4. **Normalized Quantum State Verification ($\mathcal{S}_Q$):**
   `is_normalized(tol=1e-12)` verifies $\| |\psi\rangle \| = 1.0 \pm \text{tol}$.
5. **Zero Vector Handling ($|0\rangle_{\text{vec}}$):**
   Empty state vector containing zero basis states. Norm $\| |0\rangle_{\text{vec}} \| = 0.0$. `is_normalized()` returns `False`. Normalizing $|0\rangle_{\text{vec}}$ raises `ValueError`.
6. **Immutability & Non-Aliasing:**
   State vector arithmetic operations (`+`, `-`, `*`) return new `QTMStateVector` instances without mutating operand objects.

---

## 5. Numerical Sparsification Policy vs. Mathematical Zero

> [!NOTE]
> **Core Semantic Distinction:**
> 1. **Mathematical Amplitudes:** Amplitudes are exact complex numbers $\alpha_C \in \mathbb{C}$. Exact mathematical zero is defined strictly as $\alpha_C = 0.0 + 0.0j$.
> 2. **Numerical Sparsification Policy:** For computational efficiency, the executable sparse storage model omits amplitudes whose magnitude falls within the numerical threshold ($|\alpha_C| \le \text{tol}$, default `1e-12`).
> 3. **Implementation Policy Boundary:** Numerical sparsification is a storage optimization and finite approximation policy. It does **not** alter the mathematical definition of $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$, redefine basis state equality, or establish exact unitary operator equivalence.
> 4. **Basis Equality Independence:** Basis configuration identity ($C_1 = C_2 \iff |C_1\rangle = |C_2\rangle$) is exact and strictly independent of numerical tolerance.
> 5. **Numerical Predicate Verification:** `is_normalized(tol)` and `is_zero(tol)` are numerical verification predicates under floating-point precision, not redefinitions of normalized Hilbert space state subsets.
> 6. **Future Stage Boundary:** Stage 2 sparsification policy must not be confused with exact mathematical unitary operator semantics ($U_P^\dagger U_P = I$) introduced in Stage 3 and Stage 4.

---

## 6. Public API Reference

| Module / Class / Function | Signature / Type | Description & Mathematical Contract |
| :--- | :--- | :--- |
| `QuantumBasisState` | `class` | Wrapper around `RUTMConfiguration` representing computational basis vector $|C_R\rangle$. Implements value equality and hashing. |
| `iota(config)` | `RUTMConfiguration -> QuantumBasisState` | Configuration embedding function $\iota : \mathcal{C}_R \to \mathcal{H}_Q, \iota(C_R) = |C_R\rangle$. |
| `basis_inner_product(b1, b2)` | `(QuantumBasisState, QuantumBasisState) -> complex` | Computes Dirac inner product $\langle C_1 | C_2 \rangle = \delta_{C_1, C_2}$. |
| `QTMStateVector` | `class` | Sparse state vector $|\psi\rangle = \sum \alpha_C |C_R\rangle$. Supports arithmetic, inner product, norm, and normalization. |
| `DEFAULT_TOLERANCE` | `float = 1e-12` | Centralized numerical float tolerance policy threshold for sparsification. |
| `basis_state_vector(config)` | `RUTMConfiguration -> QTMStateVector` | Factory creating normalized basis state vector $1.0 |C_R\rangle$. |
| `zero_state_vector()` | `() -> QTMStateVector` | Factory creating Hilbert space zero vector $|0\rangle_{\text{vec}}$. |

---

## 7. Implementation Scope Boundaries & Non-Goals

Stage 2 strictly excludes:
- $U_P$ unitary transition operators or matrix representations ($[U_P]$).
- Quantum state transition execution or simulation engines (`execute_qtm()`).
- Quantum circuit synthesis (Toffoli, CNOT, X gates).
- Qubit register encodings or physical qubit layout.
- External framework dependencies (NumPy, Qiskit, Cirq).

---

## 8. Verification & Regression Status

- **Module 3 Stage 2 Unit Tests:** 16 / 16 PASS (`tests/module3/test_stage2_qtm_state_model.py`)
- **Module 1 Regression:** 79 / 79 PASS
- **Module 2 Regression:** 155 / 155 PASS
- **Production Files Created:**
  - [`src/module3/qtm/basis.py`](../../src/module3/qtm/basis.py)
  - [`src/module3/qtm/state.py`](../../src/module3/qtm/state.py)
  - [`src/module3/qtm/__init__.py`](../../src/module3/qtm/__init__.py)
- **Production Files Modified:**
  - [`src/module3/__init__.py`](../../src/module3/__init__.py)
