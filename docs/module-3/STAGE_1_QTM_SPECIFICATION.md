# Stage 1 Specification — Quantum Turing Machine & Quantum Abstraction Model

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 1 — QTM & Quantum Abstraction Specification  
**Status:** NORMATIVE SPECIFICATION / FROZEN READY  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`MODULE_3_GRAPH.md`](MODULE_3_GRAPH.md)  

---

## 1. Purpose & Overview

This document establishes the formal normative mathematical specification of Module 3: the **Quantum Turing Machine (QTM) / Unitary State Machine Abstraction Layer**.

Module 3 maps discrete classical Reversible Universal Turing Machine descriptions (`RUTM-IR`) and configurations ($\mathcal{C}_R$) into a quantum computational state space ($\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$) governed by a unitary transition operator ($U_P$).

$$\text{RUTM-IR} \xrightarrow{\quad T_{RQ} \quad} \text{QTM-IR / Unitary State Machine Abstraction} \quad (U_P^\dagger U_P = I)$$

---

## 2. Terminology & Formal Notations

| Symbol / Term | Definition / Domain | Purpose |
| :--- | :--- | :--- |
| $\mathcal{C}_R$ | Set of discrete RUTM configurations | Classical configuration domain |
| $C_R$ | $C_R = (q, T, h, H, k, \text{halted}, \text{error}) \in \mathcal{C}_R$ | Single runtime machine configuration |
| $\mathcal{H}_Q$ | $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$ | Computational basis Hilbert space |
| $\mathcal{S}_Q$ | $\mathcal{S}_Q = \{ |\psi\rangle \in \mathcal{H}_Q \mid \| |\psi\rangle \| = 1.0 \}$ | Physical normalized quantum state subset |
| $|C_R\rangle$ | Basis vector in $\mathcal{H}_Q$ | Quantum computational basis state for $C_R$ |
| $\iota$ | $\iota : \mathcal{C}_R \to \mathcal{H}_Q, \quad \iota(C_R) = |C_R\rangle$ | Configuration embedding function |
| $R_P$ | $R_P : \mathcal{C}_R \to \mathcal{C}_R$ | Discrete reversible classical transition function |
| $U_P$ | $U_P = \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle C|$ | Unitary transition operator on $\mathcal{H}_Q$ |
| $[U_P]$ | $[U_P]_{N \times N}$ matrix representation | Finite verification matrix representation |
| $U_P^\dagger$ | $U_P^\dagger |R_P(C)\rangle = |C\rangle$ | Adjoint / inverse computational evolution operator |

---

## 3. Formal Configuration Domain ($\mathcal{C}_R$)

Module 3 consumes the exact classical reversible configuration model established by Module 2 Stage 2:

$$C_R = (q, T, h, H, k, \text{halted}, \text{error}) \in \mathcal{C}_R$$

where:
- $q \in \mathcal{Q}$: Current control state.
- $T : \mathbb{Z} \to \Gamma$: Tape contents function mapping tape coordinates to tape symbols.
- $h \in \mathbb{Z}$: Main tape head position coordinate.
- $H \in \mathcal{H}_{\text{stack}}$: Logical reversible history stack recording triple logs $(q_{\text{prev}}, \sigma_{\text{overwritten}}, d)$.
- $k = |H| \in \mathbb{N}$: History stack size counter ($k \ge 0$).
- $\text{halted} \in \{\text{True}, \text{False}\}$: Execution termination status flag.
- $\text{error} \in \text{Optional}[\text{str}]$: Runtime error diagnostic indicator.

> [!IMPORTANT]
> **Domain Separability:** The specification explicitly distinguishes:
> 1. `RUTM-IR`: Static program machine specification object.
> 2. $\mathcal{C}_R$: Runtime machine configuration tuple at step $t$.
> 3. Execution Trace: Sequence of configurations $[C_{R,0}, C_{R,1}, \dots, C_{R,n}]$.

---

## 4. Computational Basis Hilbert Space ($\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$)

### DEFINITION 4.1 (Hilbert Space Construction)
The quantum state space $\mathcal{H}_Q$ is the Hilbert space of square-summable complex functions over the classical configuration domain $\mathcal{C}_R$:

$$\mathcal{H}_Q = \ell^2(\mathcal{C}_R) = \left\{ |\psi\rangle = \sum_{C \in \mathcal{C}_R} \alpha_C |C\rangle \;\middle|\; \alpha_C \in \mathbb{C}, \; \sum_{C \in \mathcal{C}_R} |\alpha_C|^2 < \infty \right\}$$

### DEFINITION 4.2 (Normalized Quantum State Subset)
The subset of physical normalized quantum states $\mathcal{S}_Q \subset \mathcal{H}_Q$ consists of unit-norm vectors:

$$\mathcal{S}_Q = \left\{ |\psi\rangle \in \mathcal{H}_Q \;\middle|\; \| |\psi\rangle \| = \sqrt{\langle \psi | \psi \rangle} = 1.0 \right\}$$

### DEFINITION 4.3 (Basis Orthogonality)
For any pair of configurations $C, C' \in \mathcal{C}_R$, the computational basis states $|C\rangle, |C'\rangle \in \mathcal{H}_Q$ satisfy the Dirac inner-product orthogonality relation:

$$\langle C | C' \rangle = \delta_{C, C'} = \begin{cases} 1 & \text{if } C = C' \\ 0 & \text{if } C \neq C' \end{cases}$$

> [!NOTE]
> **Conceptual Distinction:** The specification strictly distinguishes three concepts:
> 1. **Hilbert Space $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$:** The vector space containing all square-summable complex linear combinations of basis states ($\sum |\alpha_C|^2 < \infty$).
> 2. **Arbitrary State Vector $|\psi\rangle \in \mathcal{H}_Q$:** Any element of the vector space $\mathcal{H}_Q$.
> 3. **Normalized Quantum State $|\psi\rangle \in \mathcal{S}_Q$:** A physical quantum state vector with unit norm ($\| |\psi\rangle \| = 1.0$).

---

## 5. Three Representation Tiers

The specification explicitly distinguishes three representation tiers:

1. **Tier 1 — Abstract Model ($\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$):**  
   Because the RUTM tape $T : \mathbb{Z} \to \Gamma$ is unbounded, $\mathcal{C}_R$ is countably infinite. Therefore, $\mathcal{H}_Q$ is a separable infinite-dimensional Hilbert space.
2. **Tier 2 — Finite Verification Model ($\mathcal{H}_{Q,\text{fin}} \cong \mathbb{C}^N$):**  
   For executable verification, a finite transition-closed configuration subspace $\mathcal{C}_{R,\text{fin}} \subset \mathcal{C}_R$ of size $N = |\mathcal{C}_{R,\text{fin}}|$ is used, inducing an $N$-dimensional Hilbert space $\mathcal{H}_{Q,\text{fin}} \cong \mathbb{C}^N$.
3. **Tier 3 — Physical Qubit Realization (Module 4 Target):**  
   Tensor-product qubit register encoding $|q\rangle |T\rangle |h\rangle |H\rangle |k\rangle$. *(This tier belongs strictly to Module 4 and is NOT part of Module 3)*.

---

## 6. Configuration Embedding ($\iota : \mathcal{C}_R \to \mathcal{H}_Q$)

### DEFINITION 6.1 (Embedding Function)
The configuration embedding function $\iota : \mathcal{C}_R \to \mathcal{H}_Q$ maps each classical configuration $C_R \in \mathcal{C}_R$ to its canonical computational basis vector:

$$\iota(C_R) = |C_R\rangle \in \mathcal{H}_Q$$

### PROPOSITION 6.1 (Embedding Orthogonality)
For all $C_1, C_2 \in \mathcal{C}_R$:

$$\langle \iota(C_1) | \iota(C_2) \rangle = \delta_{C_1, C_2}$$

The embedding $\iota$ forms the isometric mathematical bridge between classical reversible state space $\mathcal{C}_R$ and quantum state space $\mathcal{H}_Q$.

---

## 7. Reversible Classical Transition ($R_P : \mathcal{C}_R \to \mathcal{C}_R$)

Module 3 consumes the deterministic single-step forward transition function $R_P : \mathcal{C}_R \to \mathcal{C}_R$ established in Module 2 Stage 3:

$$C_{R,t+1} = R_P(C_{R,t})$$

Module 3 does **not** modify or redefine $R_P$; it lifts $R_P$ into quantum state space.

---

## 8. Unitary Operator Lifting ($U_P$) & Mathematical Unitarity Proof

### DEFINITION 8.1 (Unitary Transition Operator)
Let $R_P : \mathcal{C}_R \to \mathcal{C}_R$ be a reversible classical transition function. The lifted transition operator $U_P : \mathcal{H}_Q \to \mathcal{H}_Q$ is defined on basis states by:

$$U_P |C\rangle = |R_P(C)\rangle \quad \forall C \in \mathcal{C}_R$$

In outer-product operator form:

$$U_P = \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle C|$$

### THEOREM 8.1 (Unitarity of Permutation Lifting)
If the classical transition function $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection (injective and surjective), then the lifted operator $U_P$ is unitary:

$$U_P^\dagger U_P = U_P U_P^\dagger = I_{\mathcal{H}_Q}$$

#### Derivation & Proof:
1. **Adjoint Formulation:** The Hermitian adjoint $U_P^\dagger$ is:
   $$U_P^\dagger = \sum_{C' \in \mathcal{C}_R} |C'\rangle \langle R_P(C')|$$
2. **Left Unitarity ($U_P^\dagger U_P$):**
   $$U_P^\dagger U_P = \left( \sum_{C' \in \mathcal{C}_R} |C'\rangle \langle R_P(C')| \right) \left( \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle C| \right) = \sum_{C', C \in \mathcal{C}_R} |C'\rangle \langle R_P(C') | R_P(C) \rangle \langle C|$$
   By Definition 4.3, $\langle R_P(C') | R_P(C) \rangle = \delta_{R_P(C'), R_P(C)}$. Since $R_P$ is **injective**, $R_P(C') = R_P(C) \iff C' = C$. Thus:
   $$U_P^\dagger U_P = \sum_{C \in \mathcal{C}_R} |C\rangle \langle C| = I_{\mathcal{H}_Q}$$
3. **Right Unitarity ($U_P U_P^\dagger$):**
   $$U_P U_P^\dagger = \left( \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle C| \right) \left( \sum_{C' \in \mathcal{C}_R} |C'\rangle \langle R_P(C')| \right) = \sum_{C, C' \in \mathcal{C}_R} |R_P(C)\rangle \delta_{C, C'} \langle R_P(C')| = \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle R_P(C)|$$
   Since $R_P$ is **surjective**, the set $\{R_P(C) \mid C \in \mathcal{C}_R\}$ equals $\mathcal{C}_R$. Substituting $C'' = R_P(C)$:
   $$U_P U_P^\dagger = \sum_{C'' \in \mathcal{C}_R} |C''\rangle \langle C''| = I_{\mathcal{H}_Q}$$
   $\blacksquare$

---

## 9. Global Bijectivity Constraint for Halting & Error Configurations

> [!CAUTION]
> **CONDITION 9.1 (Global Bijectivity Rule):**  
> Identity extension (such as $R_P(C_{\text{halt}}) = C_{\text{halt}}$ or $R_P(C_{\text{err}}) = C_{\text{err}}$) is mathematically valid **only if** the resulting global transition relation remains total and bijective over $\mathcal{C}_R$.

### Collision Warning & Injectivity Violation:
Consider a non-terminal configuration $C_1 \neq C_{\text{halt}}$ such that $R_P(C_1) = C_{\text{halt}}$. If $C_{\text{halt}}$ also satisfies $R_P(C_{\text{halt}}) = C_{\text{halt}}$, then:

$$R_P(C_1) = R_P(C_{\text{halt}}) = C_{\text{halt}}$$

This creates a collision where two distinct configurations ($C_1 \neq C_{\text{halt}}$) map to the same image $C_{\text{halt}}$, violating injectivity ($R_P$ is not 1-to-1) and breaking unitarity ($U_P^\dagger U_P \neq I$).

### Stage 1 Formal Requirement for Terminal States:
A terminal configuration may be represented as a fixed point $R_P(C_{\text{halt}}) = C_{\text{halt}}$ **only when** the resulting global transition relation remains total and bijective over the selected configuration domain. Terminal configurations MUST participate in a globally bijective transition extension with no predecessor collision ($C_1 \neq C_{\text{halt}} \implies R_P(C_1) \neq R_P(C_{\text{halt}})$).  
*(The exact terminal state bijective encoding scheme is a **STAGE 1 FORMALIZATION REQUIREMENT** for downstream compiler implementation).*

---

## 10. History Register $H$ vs Quantum Ancilla Qubits

### DEFINITION 10.1 (Logical History vs Ancilla Workspace)
- **RUTM History Stack $H$:** A logical state variable inside computational basis state $|C_R\rangle = |q, T, h, H, k, \text{halted}, \text{error}\rangle$. It tracks classical overwrite logs to guarantee single-step reversibility $R_P^{-1}$.
- **Quantum Ancilla Qubits:** Physical auxiliary qubits allocated during quantum circuit synthesis in Module 4.
- **Uncomputation Obligation Protocol:** Module 3 models history $H$ in `QTM-IR` and specifies the formal uncomputation obligation requirement:
  $$U_P^\dagger |C_{\text{final}}\rangle = |C_0\rangle$$
  Module 4 synthesizes physical gate-level ancilla allocation and Bennett uncomputation passes.

---

## 11. Inverse / Adjoint Evolution ($U_P^\dagger$)

### DEFINITION 11.1 (Adjoint Evolution)
For a bijective transition operator $U_P$, the Hermitian adjoint $U_P^\dagger$ satisfies:

$$U_P^\dagger |R_P(C)\rangle = |C\rangle \quad \forall C \in \mathcal{C}_R$$

In embedding form:

$$U_P^\dagger \circ \iota = \iota \circ R_P^{-1}$$

> [!NOTE]
> **Terminology Requirement:** $U_P^\dagger$ represents mathematical **inverse computational evolution** (or **adjoint evolution**).  
> The specification explicitly states that $U_P^\dagger$ does **NOT** establish physical hardware time-reversal or thermodynamic time-reversal.

---

## 12. Superposition & State Norm Preservation

### DEFINITION 12.1 (Superposition Evolution)
Given an arbitrary quantum state vector $|\psi_t\rangle = \sum_{C \in \mathcal{C}_R} \alpha_C |C\rangle \in \mathcal{H}_Q$, single-step evolution under $U_P$ is defined by linearity:

$$|\psi_{t+1}\rangle = U_P |\psi_t\rangle = U_P \left( \sum_{C \in \mathcal{C}_R} \alpha_C |C\rangle \right) = \sum_{C \in \mathcal{C}_R} \alpha_C |R_P(C)\rangle$$

### THEOREM 12.1 (Norm Preservation)
For any vector $|\psi_t\rangle \in \mathcal{H}_Q$, unitary evolution under $U_P$ preserves vector norm:

$$\| U_P |\psi_t\rangle \| = \| |\psi_t\rangle \|$$

If $|\psi_t\rangle \in \mathcal{S}_Q$ (i.e. $\| |\psi_t\rangle \| = 1.0$), then $|\psi_{t+1}\rangle = U_P |\psi_t\rangle \in \mathcal{S}_Q$ (i.e. $\| |\psi_{t+1}\rangle \| = 1.0$).

---

## 13. General Quantum Dynamics Boundary

> [!IMPORTANT]
> **Permutation Unitary Boundary:**  
> Module 3 establishes permutation-style unitary evolution ($U_P |C\rangle = |R_P(C)\rangle$).  
> It does **NOT** establish arbitrary non-permutation phase gates ($e^{i\theta}$), arbitrary interference operators (Hadamard/Rotation), or general quantum circuit synthesis. These belong to Module 4.

---

## 14. Core Commuting Correspondence Theorems

### THEOREM 14.1 (Forward Commuting Correspondence Candidate)
For all $C \in \mathcal{C}_R$:

$$(U_P \circ \iota)(C) = U_P |C\rangle = |R_P(C)\rangle = \iota(R_P(C)) = (\iota \circ R_P)(C)$$

$$\mathbf{U_P \circ \iota = \iota \circ R_P}$$

```
        R_P
  C_R --------> C_R'
   |             |
   | ι           | ι
   ▼             ▼
  |C_R⟩ --U_P-> |C_R'⟩
```

### THEOREM 14.2 (Inverse Adjoint Commuting Correspondence Candidate)
For all $C' = R_P(C) \in \mathcal{C}_R$:

$$(U_P^\dagger \circ \iota)(C') = U_P^\dagger |C'\rangle = |C\rangle = \iota(R_P^{-1}(C')) = (\iota \circ R_P^{-1})(C')$$

$$\mathbf{U_P^\dagger \circ \iota = \iota \circ R_P^{-1}}$$

---

## 15. Finite Verification Model ($\mathcal{H}_{Q,\text{fin}}$) & Transition Closure

### DEFINITION 15.1 (Finite Verification Domain)
For finite-domain verification, a configuration subset $\mathcal{C}_{R,\text{fin}} \subset \mathcal{C}_R$ of size $N = |\mathcal{C}_{R,\text{fin}}|$ MUST satisfy:

$$\text{FINITE VERIFICATION DOMAIN} = \text{finite} + \text{transition-closed } (R_P(\mathcal{C}_{R,\text{fin}}) \subseteq \mathcal{C}_{R,\text{fin}}) + \text{bijective under } R_P$$

### DEFINITION 15.2 (Finite Permutation Matrix $[U_P]$)
Over $\mathcal{C}_{R,\text{fin}}$, the operator $U_P$ is represented by an $N \times N$ square permutation matrix $[U_P]$ with entries:

$$[U_P]_{i, j} = \begin{cases} 1 & \text{if } C_{R,i} = R_P(C_{R,j}) \\ 0 & \text{otherwise} \end{cases}$$

The matrix $[U_P]$ satisfies $[U_P]^\dagger [U_P] = I_{N \times N}$.

---

## 16. Formal 12-Tuple QTM Specification

### DEFINITION 16.1 (Formal QTM Abstraction Tuple)
The Module 3 Quantum Turing Machine / Unitary State Machine Abstraction is defined as the formal 12-tuple:

$$\text{QTM} = \Big( \mathcal{Q}, \Sigma, \Gamma, B, q_0, q_{\text{halt}}, \mathcal{C}_R, \mathcal{H}_Q, \iota, R_P, U_P, |\psi_0\rangle \Big)$$

where:
1. $\mathcal{Q}$: Finite set of control states (inherited from Module 2).
2. $\Sigma$: Input alphabet (inherited from Module 2).
3. $\Gamma$: Tape alphabet ($\Sigma \subset \Gamma$) (inherited from Module 2).
4. $B \in \Gamma \setminus \Sigma$: Blank symbol (inherited from Module 2).
5. $q_0 \in \mathcal{Q}$: Initial control state (inherited from Module 2).
6. $q_{\text{halt}} \in \mathcal{Q}$: Halt control state (inherited from Module 2).
7. $\mathcal{C}_R$: Set of discrete RUTM configurations $C_R = (q, T, h, H, k, \text{halted}, \text{error})$.
8. $\mathcal{H}_Q$: Hilbert space $\ell^2(\mathcal{C}_R)$ over computational basis states $|C_R\rangle$.
9. $\iota$: Configuration embedding function $\iota(C_R) = |C_R\rangle$.
10. $R_P$: Discrete reversible classical transition function (inherited from Module 2).
11. $U_P$: Unitary transition operator $U_P = \sum |R_P(C)\rangle \langle C|$ satisfying $U_P^\dagger U_P = I$.
12. $|\psi_0\rangle = \iota(C_{R,0}) = |C_{R,0}\rangle \in \mathcal{S}_Q$: Initial quantum computational basis state.

---

## 17. Discrete State Evolution Equation

$$\mathbf{|\psi_0\rangle = |C_{R,0}\rangle}, \quad \mathbf{|\psi_{t+1}\rangle = U_P |\psi_t\rangle = U_P^{t+1} |C_{R,0}\rangle = |C_{R,t+1}\rangle}$$

---

## 18. Stage 1 Non-Goals

Stage 1 explicitly does **NOT** define or include:
- Quantum circuit gate synthesis (Toffoli, CNOT, Pauli-X).
- Qubit register layouts or physical qubit mapping.
- Circuit depth optimization or transpilation passes.
- Quantum hardware backends or Qiskit/OpenQASM export.
- Physical hardware time reversal.
- Quantum error correction or fault tolerance.

---

## 19. Document Links & Portability

All document links in this specification use repository-relative paths:
- Project Constitution: [`main-technical-refference.md`](../../main-technical-refference.md)
- Root Documentation: [`README.md`](../../README.md)
- Module 3 Scope: [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md)
- Module 3 Graph: [`MODULE_3_GRAPH.md`](MODULE_3_GRAPH.md)
- Module 2 Completion: [`STAGE_9_MODULE_2_COMPLETION.md`](../module-2/STAGE_9_MODULE_2_COMPLETION.md)
