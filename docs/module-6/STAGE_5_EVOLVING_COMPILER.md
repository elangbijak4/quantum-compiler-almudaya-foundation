# Module 6 Stage 5 — Extended Gate Vocabulary & Evolving Compiler Analysis

## 1. Overview & Primary Objective

Module 6 Stage 5 establishes a formally governed, deterministic, provenance-preserving analytical framework for evaluating whether extending the compiler primitive gate vocabulary increases the expressive image of the compiler.

The baseline compiler primitive gate vocabulary is frozen as:
$$G_0 = \{X, \text{CNOT}, \text{TOFFOLI}\}$$

Given a candidate extension gate $g_c \in U(2^{n_c})$, the extended vocabulary is defined as:
$$G' = G_0 \cup \{g_c\}$$

The core research question of Stage 5 is:
$$\text{Does } |Img_N(F_{G'})| > |Img_N(F_{G0})| \quad \text{or} \quad Img_Q(F_{G0}) \subsetneq Img_Q(F_{G'})?$$

---

## 2. Mandatory Hadamard Mathematics & Superposition Verification

### 2.1 Hadamard Matrix Representation
The 1-qubit Hadamard gate $H$ is defined as:
$$H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

### 2.2 Basis State Action & Norm Residuals
Applying $H$ to standard computational basis states $|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$ and $|1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$ yields:
$$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = \begin{pmatrix} \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \end{pmatrix}, \quad H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}} = \begin{pmatrix} \frac{1}{\sqrt{2}} \\ -\frac{1}{\sqrt{2}} \end{pmatrix}$$

State vector norms satisfy:
$$\|H|0\rangle\|_2 = 1.0, \quad \|H|1\rangle\|_2 = 1.0$$
Unitarity satisfies:
$$\|H^\dagger H - I\|_F < 10^{-12}$$

### 2.3 Superposition & Complex-Amplitude Expansion
- **Superposition Generation**: Under $G_0$, all reachable computational-basis state vectors are standard basis vectors $|x\rangle$ with zero superposition. Under $G_H = G_0 \cup \{H\}$, equal-superposition states $|\psi\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$ are generated.
- **Complex Amplitude Generation**: Under $G_0$ and $G_H$, state vectors remain real-valued. Extending $G_0$ with Phase gate $S = \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix}$ or $T = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$ breaks the real-amplitude invariant and introduces complex phase amplitudes.

---

## 3. Claim-vs-Evidence Classification Scheme

Stage 5 enforces a strict, non-overclaiming classification policy for vocabulary extension claims:

| Extension Classification | Description & Conditions | Evidence Class |
| :--- | :--- | :--- |
| `ALREADY_EXPRESSIBLE` | Candidate gate $g_c$ is directly representable in baseline $G_0$. | `THEORETICAL_PROOF` |
| `REDUNDANT` | Candidate $g_c$ generates no new semantic operator classes or target coverage. | `EMPIRICAL_EXPERIMENT` |
| `EMPIRICAL_EXTENSION` | Extended vocabulary $G'$ generates new semantic operators or targets in finite sample ($|Img_N(F_{G'})| > |Img_N(F_{G0})|$), but lacks a general mathematical proof. | `EMPIRICAL_EXPERIMENT` |
| `PROVEN_EXTENSION` | Extended vocabulary $G'$ is mathematically proven to expand the infinite semantic image beyond $G_0$. | `THEORETICAL_PROOF` |
| `INCONCLUSIVE` | Search bounds or evidence are insufficient to establish extension. | `EMPIRICAL_EXPERIMENT` |

> [!IMPORTANT]
> **Mandatory Extension Policy**: Finite image expansion $|Img_N(F_{G'})| > |Img_N(F_{G0})|$ over a sample $A_N$ is **NOT** sufficient to classify `PROVEN_EXTENSION`. It establishes `EMPIRICAL_EXTENSION`. `PROVEN_EXTENSION` requires an explicit, verified mathematical proof.

---

## 4. Fundamental Invariants

1. **$G_0$ Immutability Invariant**: Baseline vocabulary $G_0 = \{X, \text{CNOT}, \text{TOFFOLI}\}$ is audited via cryptographic SHA-256 hashing before and after analysis (`hash(G0_before) == hash(G0_after)`).
2. **Backward Compatibility Invariant**: Extending vocabulary MUST preserve all baseline expressibility:
   $$Img_N(F_{G0}) \subseteq Img_N(F_{G'})$$
3. **Non-Mutation Isolation**: Stage 5 is purely an analytical subpackage (`src/module6/evolution/`) and MUST NOT perform automatic compiler promotion, primitive registry mutation, or edits to Modules 1–5.
