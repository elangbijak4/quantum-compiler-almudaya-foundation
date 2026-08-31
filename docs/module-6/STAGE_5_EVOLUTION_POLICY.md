# Module 6 Stage 5 — Compiler Evolution Policy

## 1. Scope & Governance Authority

This policy defines formal rules governing candidate gate evaluation, vocabulary extension classification, and compiler evolution.

---

## 2. Fundamental Evolution Principles

1. **Analytical Subpackage Isolation**: Stage 5 analysis operates strictly as a read-only evaluation layer (`src/module6/evolution/`). It MUST NOT mutate the active production compiler or registered primitive gate sets.
2. **Immutable Baseline $G_0$**: Baseline primitive vocabulary $G_0 = \{X, \text{CNOT}, \text{TOFFOLI}\}$ must remain frozen across all execution runs and verified via SHA-256 hashing.
3. **Backward Compatibility Guarantee**: Any candidate vocabulary extension $G' = G_0 \cup \{g_c\}$ MUST preserve all baseline expressibility:
   $$Img_N(F_{G0}) \subseteq Img_N(F_{G'})$$
4. **Mandatory Numerical Precision**: Matrix unitarity ($U^\dagger U = I, U U^\dagger = I$), state vector norms, and trace overlaps must satisfy $\epsilon = 10^{-12}$.
5. **No Overclaiming Safeguard**:
   - Finite image expansion $|Img_N(F_{G'})| > |Img_N(F_{G0})|$ over sample $A_N$ classifies ONLY as `EMPIRICAL_EXTENSION` (Evidence: `EMPIRICAL_EXPERIMENT`).
   - `PROVEN_EXTENSION` (Evidence: `THEORETICAL_PROOF`) requires an explicit, machine-checked mathematical proof covering the infinite state space.

---

## 3. Candidate Gate Submission Requirements

A candidate gate $g_c$ submitted for analysis MUST provide:
- Unique `gate_id` and descriptive `name`.
- Positive integer `arity` $n_c$.
- Square unitary matrix of dimension $2^{n_c} \times 2^{n_c}$ satisfying $\|U^\dagger U - I\|_F < 10^{-12}$ and $\|U U^\dagger - I\|_F < 10^{-12}$.
- Canonical matrix hash computed at 12 decimal places.

---

## 4. Summary of Candidate Gate Status

| Candidate Gate | Arity | Status | Action |
| :--- | :---: | :--- | :--- |
| `HADAMARD` | 1 | `EMPIRICAL_EXTENSION` | Retained as analytical candidate for quantum algorithm expressibility. |
| `PHASE_S` | 1 | `EMPIRICAL_EXTENSION` | Retained as analytical candidate for complex amplitude generation. |
| `T_GATE` | 1 | `EMPIRICAL_EXTENSION` | Retained as analytical candidate for non-Clifford phase generation. |
| `X` | 1 | `REDUNDANT` | Rejected as redundant ($X \in G_0$). |
| `CNOT` | 2 | `REDUNDANT` | Rejected as redundant ($\text{CNOT} \in G_0$). |
| `TOFFOLI` | 3 | `REDUNDANT` | Rejected as redundant ($\text{TOFFOLI} \in G_0$). |
