# Stage 6 Specification — UTM-IR & Configuration Transition Model

## 1. Overview

This document specifies the formal data structures, configuration state, and single-step transition model for the **Universal Turing Machine Intermediate Representation (UTM-IR)** in **Stage 6** of **Module 1**.

The UTM model represents a 1-tape deterministic Turing machine used as the intermediate target substrate before reversible computational modeling in future modules.

---

## 2. Mathematical Definition of UTM Components

A UTM Program is defined as a tuple:

$$M_{UTM} = (Q, \Sigma, \Gamma, \delta, q_0, B, F_{halt})$$

where:
- **$Q$**: Finite set of states (e.g., `{"q_start", "q_halt", "q1", ...}`).
- **$\Sigma$**: Input alphabet (subset of $\Gamma$).
- **$\Gamma$**: Full tape alphabet including special symbols (e.g., `{"0", "1", "_", "B", ...}`).
- **$B \in \Gamma$**: Blank symbol representing unwritten tape cells.
- **$q_0 \in Q$**: Initial start state.
- **$F_{halt} \subseteq Q$**: Set of halting states (or single canonical `q_halt`).
- **$\delta: (Q \setminus F_{halt}) \times \Gamma \to Q \times \Gamma \times \{L, R, S\}$**: Deterministic transition function.
  - Direction $L$: Move head LEFT (index $-1$).
  - Direction $R$: Move head RIGHT (index $+1$).
  - Direction $S$: STAY in place (index $+0$).

---

## 3. Configuration Representation

A UTM Machine Configuration at any discrete step $k \ge 0$ is a tuple:

$$C_k = (q, \text{tape}, h, \text{steps}, \text{halted}, \text{error})$$

where:
- **$q \in Q$**: Active state string.
- **$\text{tape}: \mathbb{Z} \to \Gamma$**: Sparse dictionary representation of infinite tape indexed by integer cell position $i \in \mathbb{Z}$. Uninitialized cells implicitly return $B$.
- **$h \in \mathbb{Z}$**: Integer tape head position index.
- **$\text{steps} \in \mathbb{N}_0$**: Step counter.
- **$\text{halted} \in \text{Bool}$**: True if $q \in F_{halt}$.
- **$\text{error} \in \text{Optional}[\text{String}]$**: Error details if transition fails (e.g. undefined transition for non-halting state).

---

## 4. Single-Step Execution Semantics $\delta(C_k) \to C_{k+1}$

Given configuration $C_k = (q, \text{tape}, h, \text{steps}, \text{halted}, \text{error})$ and program $M_{UTM}$:

1. If $\text{halted} == \text{True}$ or $\text{error} \neq \text{None}$, return $C_k$.
2. Read symbol $a = \text{tape}[h]$ (default $B$).
3. Lookup transition action $(q', a', D) = \delta(q, a)$.
   - If no transition is defined and $q \notin F_{halt}$: set $\text{error} = \text{"Undefined transition for state 'q' and symbol 'a'"}$.
4. Compute new tape: $\text{tape}'[h] = a'$.
5. Compute new head position:
   - If $D == L$: $h' = h - 1$
   - If $D == R$: $h' = h + 1$
   - If $D == S$: $h' = h$
6. Compute new state: $q' = \text{next\_state}$.
7. Check halting: $\text{halted}' = (q' == q_{halt})$.
8. Return $C_{k+1} = (q', \text{tape}', h', \text{steps} + 1, \text{halted}', \text{error}')$.

---

## 5. Stage Boundary Verification

- **Included:** UTM-IR data structures (`UTMProgram`, `UTMConfiguration`), direction enums, transition table validation, single-step transition function `step_utm_configuration()`.
- **Excluded:** AML-to-UTM automatic translation (Stage 7), full multi-step UTM simulation runner (Stage 8).
