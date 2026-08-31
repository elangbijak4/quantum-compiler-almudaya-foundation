# Stage 1 Specification — Finite Realization & Quantum Circuit Foundation

**Module:** Module 4 — Quantum Circuit Synthesis  
**Stage:** Stage 1 — Finite Realization & Quantum Circuit Foundation  
**Status:** SPECIFICATION COMPLETE / FROZEN  

---

## 1. Objective

This document establishes the formal mathematical and architectural foundation for realizing a finite configuration domain $D_\text{fin} \subset \mathcal{C}_R$ from a Quantum Turing Machine Intermediate Representation (QTM-IR) model as a finite qubit-register quantum circuit space $\mathcal{H}_n = (\mathbb{C}^2)^{\otimes n}$.

---

## 2. Input Contract

Module 4 Stage 1 consumes the frozen Module 3 QTM-IR contract:
- `QTMIRModel`
- `QTMIRBasisState`
- `QTMIRStateVector`
- `QTMIRTransitionMapping`
- `QTMIRMatrixRepresentation`
- `QTMIRProvenance`
- `validate_qtm_ir()`

Upstream Module 3 contracts are strictly read-only and immutable.

---

## 3. Finite-Domain Contract (`FiniteDomainContract`)

A finite QTM realization requires an explicit `FiniteDomainContract` specifying:
- $D_\text{fin} \subset \mathcal{C}_R$ with $|D_\text{fin}| < \infty$.
- Execution horizon $T$.
- Forward transition closure: $R_P(D_\text{fin}) \subseteq D_\text{fin}$.
- Reverse transition closure: $R_P^{-1}(D_\text{fin}) \subseteq D_\text{fin}$.
- Inclusion of the initial configuration $C_0 \in D_\text{fin}$.

Finite cardinality alone is insufficient; any domain failing forward or reverse closure under $R_P$ is rejected as unrealizable.

---

## 4. Execution-Horizon Semantics

The parameter $T \in \mathbb{N}^+$ represents the declared execution horizon. $D_\text{fin}$ must contain all classical configurations $C_t = R_P^t(C_0)$ reachable for all $t \in [0, T]$, as well as all predecessor states required for reversible execution.

---

## 5. Configuration Encoding Specification ($E$)

The mapping $E : D_\text{fin} \to \{0,1\}^n$ embeds classical configurations into $n$-bit computational basis bitstrings.

### Mathematical Invariants
1. **Strict Injectivity:** $C_1 \neq C_2 \implies E(C_1) \neq E(C_2)$ for all $C_1, C_2 \in D_\text{fin}$.
2. **Deterministic Identity:** $C_1 = C_2 \iff E(C_1) = E(C_2)$.

---

## 6. Canonical Configuration Components & History Preservation

Each configuration $C = (q, T, h, H, k, \text{halted}, \text{error})$ is encoded such that every component is preserved.

> [!IMPORTANT]
> **Logical History Preservation:** Classical history $H$ is a fundamental component of $C$. If $H_1 \neq H_2$, then $C_1 \neq C_2 \implies E(C_1) \neq E(C_2)$. Logical history MUST NOT be collapsed or confused with physical workspace ancillas.

---

## 7. Bounded Tape Window Specification

The tape space is bounded to a finite window $[M_L, M_R] \subset \mathbb{Z}$ containing $M = (M_R - M_L) + 1$ cells. Unaccessed blank cells outside $[M_L, M_R]$ are implicitly unmapped. Head position $k$ is encoded relative to $M_L$.

---

## 8. Machine-State Register ($E_Q$)

The machine control state $q \in Q$ is mapped injectively to an $n_q$-qubit register $E_Q : Q \to \{0,1\}^{n_q}$ where $n_q = \lceil \log_2 |Q| \rceil$ (or an equivalent one-hot register representation).

---

## 9. History Register

The history sequence $H = (r_1, r_2, \dots, r_k)$ is mapped into an $n_H$-qubit history register. History data remains preserved throughout execution to maintain reversibility under $R_P^{-1}$.

---

## 10. Ancilla Contract

Module 4 strictly distinguishes between:
- **Logical Configuration Registers:** (State, Tape, Head, History, Step, Status).
- **Physical Synthesis Ancillas:** Temporary workspace qubits allocated during gate realization.

### Ancilla Invariant
All physical workspace ancillas must be initialized to $|0\rangle$ and must return to $|0\rangle$ at circuit termination via Bennett uncomputation.

---

## 11. Finite Hilbert Space Embedding ($\iota_\text{fin}$)

The embedding $\iota_\text{fin} : D_\text{fin} \to \mathcal{H}_n$ maps classical configurations into computational basis states:
$$\iota_\text{fin}(C) = |E(C)\rangle$$

Since $E$ is strictly injective, distinct configurations map to orthogonal basis vectors:
$$\langle E(C_1) | E(C_2) \rangle = \delta_{C_1, C_2} \quad \forall C_1, C_2 \in D_\text{fin}$$

---

## 12. Restricted Unitary Realization ($U_C$)

The finite circuit unitary $U_C \in \text{U}(2^n)$ realizes the restriction of $U_P$ to $D_\text{fin}$ ($U_P|_{D_\text{fin}}$):
$$U_C |E(C)\rangle = |E(R_P(C))\rangle \quad \forall C \in D_\text{fin}$$

---

## 13. Basis-State Semantics

For every basis state $C \in D_\text{fin}$, the exact semantic correctness relation is:
$$U_C \iota_\text{fin}(C) = \iota_\text{fin}(R_P(C))$$

---

## 14. Superposition Semantics

By linearity, for any quantum state $|\psi\rangle = \sum_{C \in D_\text{fin}} \alpha_C |E(C)\rangle$, circuit evolution yields:
$$U_C |\psi\rangle = \sum_{C \in D_\text{fin}} \alpha_C |E(R_P(C))\rangle$$

---

## 15. Unitarity Requirements

The circuit operator $U_C$ must be strictly unitary:
$$U_C^\dagger U_C = I_{2^n} \quad \text{and} \quad U_C U_C^\dagger = I_{2^n}$$
This is guaranteed by the bijectivity of $R_P$ on the closed domain $D_\text{fin}$.

---

## 16. Canonical Primitive Gate Set

Module 4 freezes the canonical logical reversible primitive gate set:
1. **Pauli-X Gate ($X$):** Bit-flip target qubit.
2. **Controlled-NOT Gate ($\text{CNOT}$):** Bit-flip target conditioned on 1 control qubit.
3. **Toffoli Gate ($\text{Toffoli}$):** Bit-flip target conditioned on 2 control qubits.

---

## 17. Circuit-IR Boundary

`QuantumCircuitIR` is specified as a backend-independent AST representing qubit registers, gate sequences, ancilla declarations, and provenance. Schema details are subject to Stage 2 freezing.

---

## 18. Global Phase Policy

The semantic correctness relation $U_C |E(C)\rangle = |E(R_P(C))\rangle$ requires **exact computational basis state equality** without phase distortion ($\text{e}^{\text{i}\phi} \neq 1$ is prohibited for logical basis states).

---

## 19. 3-Level Numerical Verification Policy

Executable numerical verification employs a 3-level policy:
- **Level 1 (Exact Symbolic Basis Matching):** $E(R_P(C)) = \text{Permutation}(E(C))$.
- **Level 2 (State Vector Norm Comparison):** $\|\psi_\text{circuit} - \psi_\text{QTM}\|_2 < \epsilon$.
- **Level 3 (Matrix Operator Norm Comparison):** $\|U_C - U_P|_{D_\text{fin}}\|_\infty < \epsilon$.

Threshold: $\epsilon = 10^{-12}$.

---

## 20. Provenance

`QuantumCircuitIR` preserves the full compiler provenance chain:
$$\text{RUTM} \longrightarrow \text{RUTM-IR} \longrightarrow \text{QTM-IR} \longrightarrow \text{Circuit-IR}$$

---

## 21. Determinism

Synthesis is 100% deterministic. Identical inputs produce byte-for-byte identical circuit representations.

---

## 22. Invalid Realization Conditions

A realization is invalid if:
- $D_\text{fin}$ is non-finite or empty.
- $E$ is non-injective ($E(C_1) = E(C_2)$ for $C_1 \neq C_2$).
- Transition escapes $D_\text{fin}$ ($R_P(D_\text{fin}) \not\subseteq D_\text{fin}$).
- Any physical ancilla remains dirty after execution.

---

## 23. Module 4 / Module 5 Boundary & Deferred Optimization

Physical hardware routing, SWAP insertion, coupling graph transpilation, and pulse control are **FORBIDDEN** in Module 4 (reserved for Module 5). Automated depth/width optimization passes remain **DEFERRED**.
