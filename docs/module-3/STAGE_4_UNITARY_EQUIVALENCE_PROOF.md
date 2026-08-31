# Stage 4 Formal Specification & Proof Document — Unitary Equivalence, Norm Preservation & Inner-Product Invariance Theorem

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Stage:** Stage 4 — Formal Unitary Equivalence & Norm Preservation Proof  
**Status:** FORMALLY CLOSED / FROZEN  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md), [`STAGE_1_QTM_SPECIFICATION.md`](STAGE_1_QTM_SPECIFICATION.md), [`STAGE_2_QTM_STATE_MODEL.md`](STAGE_2_QTM_STATE_MODEL.md), [`STAGE_3_QTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_QTM_OPERATIONAL_SEMANTICS.md)  

---

## 1. Executive Summary & Purpose

This document contains the formal mathematical proof establishing that the lifted operational transition operator $U_P$ constructed in Stage 3:

$$U_P = \sum_{C \in \mathcal{C}_R} |R_P(C)\rangle \langle C|$$

is a **rigorously unitary operator** over the computational basis Hilbert space $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$, under the necessary and sufficient condition that the classical transition function $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection.

---

## 2. Formal Assumptions & Axiomatic Foundation

We establish the proof on the following explicit axiomatic assumptions:

- **Assumption A1 (Discrete Configuration Space):** The set of classical reversible configurations $\mathcal{C}_R$ is a non-empty discrete set.
- **Assumption A2 (Cardinality Bound):** $\mathcal{C}_R$ is either finite or countably infinite ($|\mathcal{C}_R| \le \aleph_0$).
- **Assumption A3 (Computational Basis Orthonormality):** The Hilbert space state space contains a computational basis $\{|C\rangle \mid C \in \mathcal{C}_R\}$ satisfying:
  $$\langle C | C'\rangle = \delta_{C, C'} = \begin{cases} 1 & \text{if } C = C', \\ 0 & \text{if } C \neq C'. \end{cases}$$
- **Assumption A4 (Hilbert Space Definition):** The state space $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$ consists of all square-summable complex linear combinations:
  $$|\psi\rangle = \sum_{C \in \mathcal{C}_R} \alpha_C |C\rangle \quad \text{such that} \quad \|\psi\|^2 = \sum_{C \in \mathcal{C}_R} |\alpha_C|^2 < \infty \quad (\alpha_C \in \mathbb{C}).$$
- **Assumption A5 (Total Transition Function):** $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is defined for every configuration $C \in \mathcal{C}_R$ (total domain).
- **Assumption A6 (Injectivity / No Collisions):** For all $C_1, C_2 \in \mathcal{C}_R$, $C_1 \neq C_2 \implies R_P(C_1) \neq R_P(C_2)$.
- **Assumption A7 (Surjectivity / Total Reachability):** For every $C' \in \mathcal{C}_R$, there exists at least one $C \in \mathcal{C}_R$ such that $R_P(C) = C'$.

> [!IMPORTANT]
> **Total Bijectivity Theorem:**  
> Assumptions A5, A6, and A7 together imply that $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection, possessing a unique two-sided inverse transition function $R_P^{-1} : \mathcal{C}_R \to \mathcal{C}_R$ satisfying $R_P^{-1}(R_P(C)) = C$ and $R_P(R_P^{-1}(C')) = C'$ for all $C, C' \in \mathcal{C}_R$.

---

## 3. Hilbert Space Preliminaries & Inner-Product Definition

For any two state vectors $|\psi\rangle = \sum_{C} \alpha_C |C\rangle$ and $|\phi\rangle = \sum_{C} \beta_C |C\rangle$ in $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$:

### 3.1 Inner Product
$$\langle \psi | \phi \rangle = \sum_{C \in \mathcal{C}_R} \alpha_C^* \beta_C \in \mathbb{C}$$
By Cauchy-Schwarz inequality, $|\langle \psi | \phi \rangle|^2 \le \|\psi\|^2 \|\phi\|^2 < \infty$, ensuring the inner product is well-defined.

### 3.2 Vector Norm
$$\|\psi\| = \sqrt{\langle \psi | \psi \rangle} = \sqrt{\sum_{C \in \mathcal{C}_R} |\alpha_C|^2}$$

---

## 4. Lemmas for Unitary Lifting

### Lemma 1 (Bijective Basis Permutation)
**Claim:** If $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection, then the map $|C\rangle \mapsto |R_P(C)\rangle$ is a bijective permutation of the computational basis $\{|C\rangle \mid C \in \mathcal{C}_R\}$.

**Proof:**  
1. **Injectivity:** Let $|C_1\rangle \neq |C_2\rangle \implies C_1 \neq C_2$. By Assumption A6 (injectivity of $R_P$), $R_P(C_1) \neq R_P(C_2) \implies |R_P(C_1)\rangle \neq |R_P(C_2)\rangle$.
2. **Surjectivity:** For any basis vector $|C'\rangle$, Assumption A7 guarantees $\exists C \in \mathcal{C}_R$ such that $R_P(C) = C'$. Thus $|R_P(C)\rangle = |C'\rangle$.  
Therefore, $\{|R_P(C)\rangle \mid C \in \mathcal{C}_R\} = \{|C\rangle \mid C \in \mathcal{C}_R\}$ is a complete orthonormal basis permutation. $\blacksquare$

---

### Lemma 2 (Well-Defined Linear Extension in $\ell^2(\mathcal{C}_R)$)
**Claim:** For any $|\psi\rangle = \sum_{C} \alpha_C |C\rangle \in \mathcal{H}_Q$, the linear extension $U_P |\psi\rangle = \sum_{C} \alpha_C |R_P(C)\rangle$ remains inside $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$.

**Proof:**  
Let $|\psi'\rangle = U_P |\psi\rangle = \sum_{C} \alpha_C |R_P(C)\rangle$. Perform the change of summation index $C' = R_P(C)$. Since $R_P$ is a bijection (Lemma 1), as $C$ ranges over $\mathcal{C}_R$, $C'$ ranges over $\mathcal{C}_R$ uniquely without omission or double-counting. Thus:
$$\|\psi'\|^2 = \sum_{C \in \mathcal{C}_R} |\alpha_C|^2 = \sum_{C' \in \mathcal{C}_R} |\alpha_{R_P^{-1}(C')}|^2 = \|\psi\|^2 < \infty$$
Since $\|\psi'\|^2 = \|\psi\|^2 < \infty$, $|\psi'\rangle \in \mathcal{H}_Q = \ell^2(\mathcal{C}_R)$. Thus $U_P$ is a well-defined bounded linear operator on $\mathcal{H}_Q$. $\blacksquare$

---

### Lemma 3 (Adjoint Operator Derivation)
**Claim:** The Hermitian adjoint operator $U_P^\dagger$ is given on basis vectors by:
$$U_P^\dagger |C'\rangle = |R_P^{-1}(C')\rangle \quad \forall C' \in \mathcal{C}_R$$
and outer-product form:
$$U_P^\dagger = \sum_{C' \in \mathcal{C}_R} |R_P^{-1}(C')\rangle \langle C'|$$

**Proof:**  
By definition of Hermitian adjoint, $\langle C' | U_P | C \rangle = \langle U_P^\dagger C' | C \rangle$.  
Compute the left-hand side:
$$\langle C' | U_P | C \rangle = \langle C' | R_P(C) \rangle = \delta_{C', R_P(C)}$$
Since $R_P$ is bijective, $C' = R_P(C) \iff C = R_P^{-1}(C')$. Therefore:
$$\delta_{C', R_P(C)} = \delta_{R_P^{-1}(C'), C} = \langle R_P^{-1}(C') | C \rangle$$
Equating $\langle U_P^\dagger C' | C \rangle = \langle R_P^{-1}(C') | C \rangle$ for all $C \in \mathcal{C}_R$ yields:
$$U_P^\dagger |C'\rangle = |R_P^{-1}(C')\rangle \quad \blacksquare$$

---

## 5. Main Theorems

### Theorem 1 (Left Unitarity $U_P^\dagger U_P = I_{\mathcal{H}_Q}$)
**Theorem Statement:** If $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection, then $U_P^\dagger U_P = I_{\mathcal{H}_Q}$.

**Proof:**  
1. **Basis Evaluation:** For any basis state $|C\rangle \in \mathcal{H}_Q$:
   $$U_P^\dagger U_P |C\rangle = U_P^\dagger |R_P(C)\rangle$$
   Applying Lemma 3 with $C' = R_P(C)$:
   $$U_P^\dagger |R_P(C)\rangle = |R_P^{-1}(R_P(C))\rangle = |C\rangle$$
   Thus $U_P^\dagger U_P |C\rangle = |C\rangle = I_{\mathcal{H}_Q} |C\rangle$ for all basis states $|C\rangle$.
2. **Linear Extension:** For any state $|\psi\rangle = \sum_{C} \alpha_C |C\rangle \in \mathcal{H}_Q$:
   $$U_P^\dagger U_P |\psi\rangle = U_P^\dagger U_P \left( \sum_{C \in \mathcal{C}_R} \alpha_C |C\rangle \right) = \sum_{C \in \mathcal{C}_R} \alpha_C \left( U_P^\dagger U_P |C\rangle \right) = \sum_{C \in \mathcal{C}_R} \alpha_C |C\rangle = |\psi\rangle$$
   Therefore, $U_P^\dagger U_P = I_{\mathcal{H}_Q}$. $\blacksquare$

---

### Theorem 2 (Right Unitarity $U_P U_P^\dagger = I_{\mathcal{H}_Q}$)
**Theorem Statement:** If $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection, then $U_P U_P^\dagger = I_{\mathcal{H}_Q}$.

**Proof:**  
1. **Basis Evaluation:** For any basis state $|C'\rangle \in \mathcal{H}_Q$:
   $$U_P U_P^\dagger |C'\rangle = U_P |R_P^{-1}(C')\rangle$$
   Applying the definition of $U_P$ with basis vector $|R_P^{-1}(C')\rangle$:
   $$U_P |R_P^{-1}(C')\rangle = |R_P(R_P^{-1}(C'))\rangle$$
   By surjectivity of $R_P$ (Assumption A7), $R_P(R_P^{-1}(C')) = C'$. Thus:
   $$U_P U_P^\dagger |C'\rangle = |C'\rangle = I_{\mathcal{H}_Q} |C'\rangle$$
2. **Linear Extension:** By linearity over $\mathcal{H}_Q$:
   $$U_P U_P^\dagger |\phi\rangle = |\phi\rangle \quad \forall |\phi\rangle \in \mathcal{H}_Q$$
   Therefore, $U_P U_P^\dagger = I_{\mathcal{H}_Q}$. $\blacksquare$

> [!NOTE]
> **Role of Surjectivity:** In infinite-dimensional Hilbert spaces, $U^\dagger U = I$ alone only guarantees that $U$ is an isometry. The independent proof of $U U^\dagger = I$ requires surjectivity of $R_P$, confirming that $U_P$ is surjective and thus a full unitary operator.

---

### Theorem 3 (Main Unitarity Theorem)
**Theorem Statement:** If $R_P : \mathcal{C}_R \to \mathcal{C}_R$ is a total bijection, then the lifted transition operator $U_P = \sum_{C} |R_P(C)\rangle \langle C|$ is a unitary operator on $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$.

**Proof:**  
By Theorem 1 ($U_P^\dagger U_P = I_{\mathcal{H}_Q}$) and Theorem 2 ($U_P U_P^\dagger = I_{\mathcal{H}_Q}$), $U_P$ is invertible with $U_P^{-1} = U_P^\dagger$. By definition of unitary operators in Hilbert space, $U_P$ is unitary. $\blacksquare$

---

### Theorem 4 (Norm Preservation)
**Theorem Statement:** For all $|\psi\rangle \in \mathcal{H}_Q$, $\|U_P \psi\| = \|\psi\|$.

**Proof:**  
$$\|U_P \psi\|^2 = \langle U_P \psi | U_P \psi \rangle = \langle \psi | U_P^\dagger U_P | \psi \rangle$$
Applying Theorem 1 ($U_P^\dagger U_P = I_{\mathcal{H}_Q}$):
$$\langle \psi | I_{\mathcal{H}_Q} | \psi \rangle = \langle \psi | \psi \rangle = \|\psi\|^2$$
Taking positive square roots yields $\|U_P \psi\| = \|\psi\|$. $\blacksquare$

---

### Theorem 5 (Inner-Product Preservation)
**Theorem Statement:** For all $|\psi\rangle, |\phi\rangle \in \mathcal{H}_Q$, $\langle U_P \psi | U_P \phi \rangle = \langle \psi | \phi \rangle$.

**Proof:**  
$$\langle U_P \psi | U_P \phi \rangle = \langle \psi | U_P^\dagger U_P | \phi \rangle = \langle \psi | I_{\mathcal{H}_Q} | \phi \rangle = \langle \psi | \phi \rangle \quad \blacksquare$$

---

### Theorem 6 (Orthonormal Basis Preservation)
**Theorem Statement:** For all $C_1, C_2 \in \mathcal{C}_R$, $\langle U_P C_1 | U_P C_2 \rangle = \delta_{C_1, C_2}$.

**Proof:**  
$$\langle U_P C_1 | U_P C_2 \rangle = \langle R_P(C_1) | R_P(C_2) \rangle = \delta_{R_P(C_1), R_P(C_2)}$$
By Assumption A6 (injectivity of $R_P$), $R_P(C_1) = R_P(C_2) \iff C_1 = C_2$.  
Therefore, $\delta_{R_P(C_1), R_P(C_2)} = \delta_{C_1, C_2}$. $\blacksquare$

---

## 6. Compiler Semantic Preservation Theorems

### Theorem 7 (Forward Commuting Correspondence)
**Theorem Statement:** $\mathbf{U_P \circ \iota = \iota \circ R_P}$

**Proof:**  
For any configuration $C \in \mathcal{C}_R$:
- Path A: $(\iota \circ R_P)(C) = \iota(R_P(C)) = |R_P(C)\rangle$
- Path B: $(U_P \circ \iota)(C) = U_P(\iota(C)) = U_P |C\rangle = |R_P(C)\rangle$  
Since Path A = Path B for all $C \in \mathcal{C}_R$, $U_P \circ \iota = \iota \circ R_P$. $\blacksquare$

```
        R_P
  C_R --------> C_R'
   |             |
   | ι           | ι
   ▼             ▼
  |C_R⟩ --U_P-> |C_R'⟩
```

---

### Theorem 8 (Adjoint Reverse Commuting Correspondence)
**Theorem Statement:** $\mathbf{U_P^\dagger \circ \iota = \iota \circ R_P^{-1}}$

**Proof:**  
For any configuration $C' \in \mathcal{C}_R$:
- Path A: $(\iota \circ R_P^{-1})(C') = \iota(R_P^{-1}(C')) = |R_P^{-1}(C')\rangle$
- Path B: $(U_P^\dagger \circ \iota)(C') = U_P^\dagger(\iota(C')) = U_P^\dagger |C'\rangle = |R_P^{-1}(C')\rangle$ (by Lemma 3)  
Since Path A = Path B for all $C' \in \mathcal{C}_R$, $U_P^\dagger \circ \iota = \iota \circ R_P^{-1}$. $\blacksquare$

---

## 7. Domain & Extension Corollaries

### Corollary 1 (Finite-Domain Restrictions)
Let $D \subset \mathcal{C}_R$ be a finite transition-closed domain ($R_P(D) = D$) of size $N = |D|$. If $R_P|_D : D \to D$ is bijective, then the finite restriction operator $U_P|_{\mathcal{H}_D}$ over subspace $\mathcal{H}_D = \text{span}\{|C\rangle \mid C \in D\}$ is unitary. Its matrix representation $[U_P]_{N \times N}$ over an ordered basis $[b_0, \dots, b_{N-1}]$ is an $N \times N$ permutation matrix satisfying:
$$[U_P]^\dagger [U_P] = I_{N \times N} \quad \text{and} \quad [U_P] [U_P]^\dagger = I_{N \times N}$$

### Corollary 2 (Identity Extension over Complementary Domain)
Let $D \subset \mathcal{C}_R$ be finite and $M : D \to D$ be a bijection. Define the global transition extension $R_{\text{ext}} : \mathcal{C}_R \to \mathcal{C}_R$ by:
$$R_{\text{ext}}(C) = \begin{cases} M(C) & \text{if } C \in D, \\ C & \text{if } C \in \mathcal{C}_R \setminus D. \end{cases}$$
Because $\mathcal{C}_R = D \sqcup (\mathcal{C}_R \setminus D)$ is a disjoint union and $M|_D$ and $\text{id}|_{\mathcal{C}_R \setminus D}$ are both bijections on their respective disjoint components, $R_{\text{ext}}$ is a total bijection on $\mathcal{C}_R$. Thus the lifted global operator $U_{\text{ext}}$ is globally unitary on $\mathcal{H}_Q = \ell^2(\mathcal{C}_R)$.

---

## 8. Counterexample & Necessity Analysis

### 8.1 Injectivity Failure (Collisions)
Suppose $C_1 \neq C_2$ but $R_P(C_1) = R_P(C_2) = C^*$.
Then $U_P |C_1\rangle = |C^*\rangle$ and $U_P |C_2\rangle = |C^*\rangle$.
Compute inner product:
$$\langle U_P C_1 | U_P C_2 \rangle = \langle C^* | C^* \rangle = 1.0 \neq \delta_{C_1, C_2} = 0.0$$
Preservation of orthogonality fails. Furthermore, $U_P^\dagger |C^*\rangle$ cannot map uniquely to both $|C_1\rangle$ and $|C_2\rangle$, breaking $U_P^\dagger U_P = I$. Thus injectivity is **strictly necessary**.

### 8.2 Surjectivity Failure (Unreachable Basis States)
Suppose some configuration $C_{\text{target}} \in \mathcal{C}_R$ has no predecessor ($R_P(C) \neq C_{\text{target}}$ for all $C \in \mathcal{C}_R$).
Then $U_P^\dagger |C_{\text{target}}\rangle = |R_P^{-1}(C_{\text{target}})\rangle$ is undefined / empty, and $U_P U_P^\dagger |C_{\text{target}}\rangle = 0 \neq |C_{\text{target}}\rangle$, breaking $U_P U_P^\dagger = I$. Thus surjectivity is **strictly necessary**.

---

## 9. Scope Boundary & Non-Goals

The mathematical theorems established in Stage 4 prove that classical reversible transitions lift to permutation-style unitary operators over configuration-indexed Hilbert spaces. Stage 4 explicitly **excludes**:
- Arbitrary phase dynamics (such as Hadamard gates $\frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$ or $R_\theta$ rotations).
- Physical qubit encoding layouts, bitstring registers, or multi-qubit tensor products.
- Quantum circuit gate synthesis or transpilation (Module 4 target).

---

## 10. Relation to Executable Model & Formal Conclusion

The formal mathematical proofs in this document establish the universal mathematical foundation ($\forall |\psi\rangle \in \mathcal{H}_Q$), while executable software tests (`tests/module3/test_stage3_unitary_operator.py` and `tests/module3/test_stage4_unitary_proof.py`) provide automated verification witnesses on finite transition-closed domains.

**Formal Conclusion:**  
Module 3 Stage 4 is **FORMALLY COMPLETE AND FROZEN**. All unitary equivalence, norm preservation, inner-product preservation, and commuting correspondence theorems are rigorously established.
