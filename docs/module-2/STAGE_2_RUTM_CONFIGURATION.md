# Stage 2 Formalization — RUTM Configuration Model

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 2 — RUTM Configuration Model  
**Status:** COMPLETE  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`STAGE_1_RUTM_SPECIFICATION.md`](STAGE_1_RUTM_SPECIFICATION.md)  

---

## 1. Purpose

The purpose of Stage 2 is to transform the Stage 1 mathematical specification into a precise, internally consistent, formal configuration space and representation model for the **Reversible Universal Turing Machine (RUTM)**.

Stage 2 answers with formal mathematical rigor:
1. What exactly constitutes a valid RUTM configuration?
2. What exact information is required to deterministically advance and reverse execution?
3. What representation invariants bind the configuration elements?
4. How does the extended configuration project onto the frozen Module 1 UTM configuration space?

---

## 2. Scope

### In-Scope:
- Formal Cartesian product definition of RUTM configuration space $\mathcal{C}_R$.
- Rigorous domain, codomain, invariants, allowed values, and equality semantics for all 7 components of $C_R = (q, T, h, H, k, \text{halted}, \text{error})$.
- Representation invariant $k = |H|$.
- Mathematical and sparse-dictionary tape models, head movement function and inverse.
- Formal history space $\mathcal{H}$, history record tuple $\text{Record}$, and stack operations ($\text{Push}, \text{Pop}, \text{Top}, |\cdot|$).
- Formal definition of the reversible domain $\text{Dom}(R_{\text{rev}})$ and image $\text{Im}(R_{\text{rev}})$.
- Valid Configuration Predicate $\text{Valid\_RUTM}(C_R)$.
- Formal projection function $\pi_{\text{UTM}} : \mathcal{C}_R \to \mathcal{C}_{\text{UTM}}$ into Module 1's frozen `UTMConfiguration`.
- Formulation of the commuting diagram $\pi_{\text{UTM}} \circ R = \delta \circ \pi_{\text{UTM}}$ and proof obligations for Stage 3/4.
- Minimal executable data-model module `src/module2/rutm/model.py` and test suite `tests/module2/test_stage2_rutm_model.py`.

### Out-of-Scope:
- Step transition execution engine (belongs to Stage 3 / Stage 7).
- Translator $T_2 : \text{UTM-IR} \to \text{RUTM-IR}$ (Stage 6).
- Full forward/reverse execution simulator (Stage 7).
- Modification of frozen Module 1 source, tests, or certificates.
- Premature claims of universal reversibility proof or thermodynamic reversibility.

---

## 3. Formal Configuration Space ($\mathcal{C}_R$)

The formal configuration space $\mathcal{C}_R$ of a Reversible Universal Turing Machine defined over control states $Q$ and tape alphabet $\Gamma$ is the Cartesian product:

$$\mathcal{C}_R = Q \times \text{Tape} \times \text{Head} \times \text{History} \times \text{Counter} \times \text{HaltState} \times \text{ErrorState}$$

where:
- $Q$: finite set of control states.
- $\text{Tape} = \{ T : \mathbb{Z} \to \Gamma \mid \{ z \in \mathbb{Z} \mid T(z) \neq B \} \text{ is finite} \}$.
- $\text{Head} = \mathbb{Z}$.
- $\text{History} = \mathcal{H} = \text{Sequence}[\text{Record}]$ where $\text{Record} = Q \times \Gamma \times \{L, R, S\}$.
- $\text{Counter} = \mathbb{N}_0 = \{0, 1, 2, 3, \dots\}$.
- $\text{HaltState} = \{\text{True}, \text{False}\}$.
- $\text{ErrorState} = \text{Optional}[\text{str}] = \text{String} \cup \{\text{None}\}$.

An element of $\mathcal{C}_R$ is written as the 7-tuple:
$$C_R = (q, T, h, H, k, \text{halted}, \text{error})$$

---

## 4. Component Domains & Specifications

| Component | Formal Type | Mathematical Domain | Semantic Meaning | Invariants & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **$q$** | `str` | $Q$ | Current control state | $q \in Q$; non-empty string identifier. |
| **$T$** | `Dict[int, str]` | $\mathbb{Z} \to \Gamma$ | Main tape memory mapping | Finite support: non-blank cells finite; $T(z) \in \Gamma$. |
| **$h$** | `int` | $\mathbb{Z}$ | Main tape head position | Integer cell coordinate ($-\infty < h < \infty$). |
| **$H$** | `Tuple[Record, ...]` | $\mathcal{H} = \bigcup_{m=0}^\infty (Q \times \Gamma \times \{L,R,S\})^m$ | Auxiliary history log | Sequence of predecessor records $r = (q_{\text{prev}}, s_{\text{overwritten}}, d_{\text{prev}})$. |
| **$k$** | `int` | $\mathbb{N}_0$ | Execution step counter | $k = |H|$; non-negative integer. |
| **$\text{halted}$** | `bool` | $\{\text{True}, \text{False}\}$ | Halting status flag | Consistent with control state: $\text{halted} = \text{True} \iff q = q_{\text{halt}}$. |
| **$\text{error}$** | `Optional[str]` | $\text{String} \cup \{\text{None}\}$ | Execution error string | Must be `None` for configurations in $\text{Dom}(R_{\text{rev}})$. |

---

## 5. Tape Model

### 5.1 Mathematical Tape vs. Implementation Representation

- **Mathematical Tape ($T$):** Infinite function $T : \mathbb{Z} \to \Gamma$ mapping every integer position $z \in \mathbb{Z}$ to a tape symbol, with blank symbol $B = "\_"$.
- **Implementation Tape ($T_{\text{dict}}$):** Finite sparse dictionary `Dict[int, str]` containing only cells explicitly written or read. For any $z \notin \text{keys}(T_{\text{dict}})$, $T(z) = B = "\_"$.

### 5.2 Tape Operations

- **Read Symbol:**
  $$\text{Read}(T, z) = T(z) = T_{\text{dict}}.\text{get}(z, "\_")$$
- **Write Symbol:**
  $$\text{Write}(T, z, s') = T'[y] = \begin{cases} s' & \text{if } y = z \\ T(y) & \text{if } y \neq z \end{cases}$$
  In sparse dictionary implementation, if $s' = "\_"$ and $z \in T_{\text{dict}}$, $z$ may remain or be stored as $"\_"$.

### 5.3 Extensional Tape Equality

Two mathematical tapes $T_1$ and $T_2$ are extensionally equal ($T_1 = T_2$) if and only if:
$$\forall z \in \mathbb{Z}, \quad T_1(z) = T_2(z)$$
For implementation dictionaries $T_{\text{dict},1}$ and $T_{\text{dict},2}$, extensional equality holds iff for all $z \in \text{keys}(T_{\text{dict},1}) \cup \text{keys}(T_{\text{dict},2})$, $T_1(z) = T_2(z)$.

---

## 6. Head Model

The head position $h$ is an unrestricted integer $h \in \mathbb{Z}$.

### 6.1 Movement Functions
Direction $d \in \{L, R, S\}$ (where $L = \text{LEFT}, R = \text{RIGHT}, S = \text{STAY}$):
$$\text{move}(h, L) = h - 1$$
$$\text{move}(h, R) = h + 1$$
$$\text{move}(h, S) = h$$

### 6.2 Inverse Movement Function
$$\text{inverse\_move}(h', L) = h' + 1$$
$$\text{inverse\_move}(h', R) = h' - 1$$
$$\text{inverse\_move}(h', S) = h'$$

### 6.3 Inversion Identity Theorem
For all head positions $h \in \mathbb{Z}$ and all directions $d \in \{L, R, S\}$:
$$\text{inverse\_move}(\text{move}(h, d), d) = h$$

---

## 7. Control State Model

Control states belong to finite set $Q$:
- $q_{\text{start}} \in Q$: initial control state.
- $q_{\text{halt}} \in Q$: halting control state.
- $Q_{\text{ord}} = Q \setminus \{q_{\text{halt}}\}$: ordinary computational states.

### Consistency Invariant:
In every valid execution configuration:
$$\text{halted} = \text{True} \iff q = q_{\text{halt}}$$
This invariant ensures no ambiguity exists between state-based halting and flag-based halting.

---

## 8. History Model ($\mathcal{H}$)

### 8.1 History Record Tuple
A single transition record $r \in \text{Record}$ is defined as the immutable 3-tuple:
$$r = (q_{\text{prev}}, s_{\text{overwritten}}, d_{\text{prev}}) \in Q \times \Gamma \times \{L, R, S\}$$
- $q_{\text{prev}} \in Q$: exact control state of the predecessor configuration.
- $s_{\text{overwritten}} \in \Gamma$: exact symbol that occupied cell $h_{\text{prev}}$ before the write operation.
- $d_{\text{prev}} \in \{L, R, S\}$: exact head movement direction performed during the forward step.

### 8.2 History Space & Stack Operations
History sequence $H \in \mathcal{H}$:
- $\text{EmptyHistory} = []$
- $\text{Push}(H, r) = H \mathbin{+\!\!+} [r]$
- $\text{Pop}(H \mathbin{+\!\!+} [r]) = (H, r)$
- $\text{Top}(H \mathbin{+\!\!+} [r]) = r$
- $\text{Length}(H) = |H| \in \mathbb{N}_0$

---

## 9. Representation Invariant ($k = |H|$)

Every valid RUTM configuration must strictly satisfy:

$$k = |H|$$

- $k$ is an explicit integer field in $C_R$ to match standard step counting interfaces.
- $|H|$ is the length of the history sequence.
- **Dependency Invariant:** Any configuration where $k \neq |H|$ is malformed and fails the $\text{Valid\_RUTM}(C_R)$ predicate.

---

## 10. Halt Model & Terminal Execution Boundary

- When $q = q_{\text{halt}}$ and $\text{halted} = \text{True}$, forward transition $R(C_R)$ behaves as a terminal fixed point:
  $$R(C_R) = C_R$$
- However, $C_R$ retains its history log $H$. Reverse transition $R^{-1}(C_R)$ pops the final transition record from $H$, stepping backward out of $q_{\text{halt}}$ into the exact predecessor state $q_{k-1} \in Q_{\text{ord}}$.

---

## 11. Error Model & Status

- $\text{error} \in \text{Optional}[\text{str}]$ captures runtime failures (e.g. undefined transitions).
- If $\text{error} \neq \text{None}$, the configuration is an **Error Configuration**.
- Error configurations are explicitly outside the reversible domain $\text{Dom}(R_{\text{rev}})$. Forward and reverse transitions on error configurations return the error configuration unchanged (halted error state).

---

## 12. Configuration Equality ($\stackrel{R}{=}$)

Two configurations $C_R^{(1)}$ and $C_R^{(2)}$ are equal ($C_R^{(1)} = C_R^{(2)}$) if and only if:
$$q_1 = q_2 \land h_1 = h_2 \land k_1 = k_2 \land \text{halt}_1 = \text{halt}_2 \land e_1 = e_2 \land H_1 = H_2 \land (\forall z \in \mathbb{Z}, T_1(z) = T_2(z))$$

---

## 13. Initial Configuration ($C_{R,0}$)

Given input tape $T_0$ and initial state $q_{\text{start}}$:

$$C_{R,0} = (q_{\text{start}}, T_0, 0, [], 0, \text{False}, \text{None})$$

### Initial Invariants:
- $|H_0| = 0$
- $k_0 = 0$
- $h_0 = 0$
- $\text{halted}_0 = \text{False}$
- $\text{error}_0 = \text{None}$

---

## 14. Valid Configuration Predicate ($\text{Valid\_RUTM}(C_R)$)

The formal validation predicate $\text{Valid\_RUTM}(C_R) \in \{\text{True}, \text{False}\}$ evaluates to $\text{True}$ if and only if all of the following conditions hold:

$$\begin{aligned}
\text{Valid\_RUTM}(C_R) \iff & (q \in Q) \land (h \in \mathbb{Z}) \land (k \in \mathbb{N}_0) \land (|H| = k) \\
& \land (\text{halted} \in \{\text{True}, \text{False}\}) \land (\text{halted} = \text{True} \iff q = q_{\text{halt}}) \\
& \land (\forall z \in \text{keys}(T), T(z) \in \Gamma) \\
& \land (\forall (q_i, s_i, d_i) \in H, q_i \in Q \land s_i \in \Gamma \land d_i \in \{L, R, S\})
\end{aligned}$$

---

## 15. Reversible Domain ($\text{Dom}(R_{\text{rev}})$) & Image ($\text{Im}(R_{\text{rev}})$)

The domain of the reversible transition function is:
$$\text{Dom}(R_{\text{rev}}) = \{ C_R \in \mathcal{C}_R \mid \text{Valid\_RUTM}(C_R) \land \text{error} = \text{None} \land \text{halted} = \text{False} \land \exists \delta(q, T(h)) \}$$

The image (codomain) of forward transition on $\text{Dom}(R_{\text{rev}})$ is:
$$\text{Im}(R_{\text{rev}}) = \{ C'_R \in \mathcal{C}_R \mid \exists C_R \in \text{Dom}(R_{\text{rev}}), R(C_R) = C'_R \}$$

The inverse transition function is defined on $\text{Im}(R_{\text{rev}})$:
$$R^{-1} : \text{Im}(R_{\text{rev}}) \longrightarrow \text{Dom}(R_{\text{rev}})$$

---

## 16. Projection to UTM ($\pi_{\text{UTM}}$)

The canonical projection function $\pi_{\text{UTM}} : \mathcal{C}_R \to \mathcal{C}_{\text{UTM}}$ maps an extended RUTM configuration $C_R$ directly onto Module 1's frozen `UTMConfiguration` space:

$$\pi_{\text{UTM}}(q, T, h, H, k, \text{halted}, \text{error}) = (q, T, h, k, \text{halted}, \text{error})$$

### Codomain Verification:
The output of $\pi_{\text{UTM}}(C_R)$ matches the exact signature and fields of `src.module1.utm.model.UTMConfiguration`:
- `current_state`: `q`
- `tape`: `T`
- `head_pos`: `h`
- `step_count`: `k`
- `halted`: `halted`
- `error`: `error`

---

## 17. Projection Invariant & Commuting Diagram

### 17.1 Projection Invariant
For any RUTM execution configuration $C_{R,k}$ at step $k$:
$$\pi_{\text{UTM}}(C_{R,k}) = C_k$$
where $C_k$ is the step-$k$ configuration of the source UTM.

### 17.2 Commuting Diagram
```
                         R
        C_R  ----------------------> C'_R
         |                              |
  π_UTM  |                              | π_UTM
         ▼                              ▼
        C   ---------------------->  C'
                         δ
```

### 17.3 Commuting Relation Statement (Proof Obligation for Stage 3/4)
$$\forall C_R \in \text{Dom}(R_{\text{rev}}), \quad \pi_{\text{UTM}}(R(C_R)) = \delta(\pi_{\text{UTM}}(C_R))$$

---

## 18. ForwardStep & ReverseStep Transition Contracts

### 18.1 ForwardStep Contract
- **Input Domain:** $C_R \in \text{Dom}(R_{\text{rev}})$, transition table $\delta$.
- **Preconditions:** $\text{Valid\_RUTM}(C_R) = \text{True}$, $\text{error} = \text{None}$, $\text{halted} = \text{False}$, $\delta(q, T(h)) = (q', s', d)$.
- **Postconditions:**
  - $C'_R = (q', T', h', H \mathbin{+\!\!+} [(q, T(h), d)], k+1, (q' == q_{\text{halt}}), \text{None})$.
  - $\text{Valid\_RUTM}(C'_R) = \text{True}$.
  - $|H'| = k + 1$.
  - $\pi_{\text{UTM}}(C'_R) = \delta(\pi_{\text{UTM}}(C_R))$.

### 18.2 ReverseStep Contract
- **Input Domain:** $C'_R \in \text{Im}(R_{\text{rev}})$.
- **Preconditions:** $\text{Valid\_RUTM}(C'_R) = \text{True}$, $k' > 0$, $H' \neq []$, top record $r = (q, s, d)$.
- **Postconditions:**
  - $C_R = (q, T, h, H, k'-1, \text{False}, \text{None})$.
  - $\text{Valid\_RUTM}(C_R) = \text{True}$.
  - $R(C_R) = C'_R$.

---

## 19. Proof Obligations Formulated for Stage 3 / Stage 4

1. **Obligation 1 (Configuration Validation Invariance):** Prove that if $\text{Valid\_RUTM}(C_R)$ holds and $C_R \in \text{Dom}(R_{\text{rev}})$, then $\text{Valid\_RUTM}(R(C_R))$ holds.
2. **Obligation 2 (Commutativity with UTM):** Prove that $\pi_{\text{UTM}}(R(C_R)) = \delta(\pi_{\text{UTM}}(C_R))$.
3. **Obligation 3 (Exact Predecessor Recovery):** Prove that $R^{-1}(R(C_R)) = C_R$ for all $C_R \in \text{Dom}(R_{\text{rev}})$.

---

## 20. Non-Claims & Explicit Boundaries

1. **No Thermodynamic Claim:** Logical history tracking does NOT imply zero physical energy dissipation.
2. **No Universal Theorem Claimed at Stage 2:** Commutativity and invertibility are formulated as contracts and proof obligations; universal proofs belong to Stage 4.
3. **No Modification of Module 1:** Module 1 source code and tests remain untouched and frozen.

---

## 21. Stage 3 Prerequisites

Before proceeding to **Stage 3 (Reversible Operational Semantics)**:
1. Verify `src/module2/rutm/model.py` passes all configuration data-model unit tests.
2. Verify frozen Module 1 regression test suite (79/79 PASS).
3. Obtain explicit user authorization to advance to Stage 3.
