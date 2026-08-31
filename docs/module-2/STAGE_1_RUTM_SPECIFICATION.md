# Stage 1 Specification — Reversible Universal Turing Machine (RUTM) Model

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 1 — RUTM Specification  
**Status:** COMPLETE  
**Governing Document:** [`main-technical-refference.md`](../../main-technical-refference.md)  
**Input Specification:** Module 1 UTM-IR ([`docs/module-1/STAGE_6_UTM_IR.md`](../module-1/STAGE_6_UTM_IR.md), [`src/module1/utm/model.py`](../../src/module1/utm/model.py))  

---

## 1. Purpose

The purpose of Stage 1 is to establish the formal mathematical definition, state configuration tuple, forward transition function, computable inverse transition function, history/auxiliary tracking model, reversibility proof obligations, and boundary claims for the **Reversible Universal Turing Machine (RUTM)** model in Module 2.

This document serves as the authoritative mathematical contract for the transformation edge:
$$T_2 : \text{UTM-IR} \longrightarrow \text{Reversible-UTM-IR}$$

---

## 2. Scope

### In-Scope (Stage 1 Authorized Work):
- Formal 8-tuple specification of the RUTM computational model.
- Extended RUTM configuration tuple $C_R = (q, T, h, H, k, \text{halted}, \text{error})$.
- Forward transition relation $R : \mathcal{C}_R \to \mathcal{C}_R$.
- Reverse transition relation $R^{-1} : \mathcal{C}_R \to \mathcal{C}_R$.
- Rigorous definition of logical and computational reversibility.
- Auxiliary history stack/log model $H$ and predecessor restoration proof.
- Preservation boundary of observable UTM semantics ($Obs_{\text{UTM}} \equiv Obs_{\text{RUTM}}$).
- Formal proof obligations for Stage 4 reversibility theorem.
- Informational efficiency overhead metrics (history growth, step expansion).

### Out-of-Scope (Strictly Prohibited in Stage 1 & Module 2):
- Code implementation of RUTM translator, RUTM simulator, or C2 generator (belongs to Stage 5–12).
- Quantum Turing Machines (QTM / QUTM) or quantum gates/circuits (Module 3 & 4).
- Thermodynamic reversibility claims (e.g. Landauer limit zero-dissipation claims).
- Modification of frozen Module 1 source code (`src/module1/`), tests (`tests/module1/`), or Certificate C1 artifacts.

---

## 3. UTM Input Model (Frozen Module 1 Contract)

Module 2 consumes the deterministic 7-tuple Universal Turing Machine representation established in Module 1 Stage 6 ([`src/module1/utm/model.py`](../../src/module1/utm/model.py)):

$$\text{UTM} = (Q, \Sigma, \Gamma, \delta, q_{\text{start}}, B, q_{\text{halt}})$$

where:
- $Q$: finite set of control states.
- $\Sigma$: input alphabet ($\Sigma \subset \Gamma$).
- $\Gamma$: finite tape alphabet including blank symbol $B = "\_"$.
- $\delta : (Q \setminus \{q_{\text{halt}}\}) \times \Gamma \to Q \times \Gamma \times \{L, R, S\}$: deterministic transition function.
- $q_{\text{start}} \in Q$: initial control state.
- $B = "\_" \in \Gamma$: blank symbol.
- $q_{\text{halt}} \in Q$: halting control state.

A standard UTM configuration is $C = (q, T, h, k, \text{halted}, \text{error})$ where $q \in Q$, $T : \mathbb{Z} \to \Gamma$, $h \in \mathbb{Z}$, and $k \in \mathbb{N}_0$.

---

## 4. RUTM Definition

A **Reversible Universal Turing Machine (RUTM)** in Module 2 is specified as an 8-tuple:

$$\text{RUTM} = (Q_R, \Sigma_R, \Gamma_R, \delta_R, \delta_R^{-1}, q_{\text{start}}, B, q_{\text{halt}})$$

where:
1. $Q_R = Q$: control state set identical to source UTM.
2. $\Sigma_R = \Sigma$: input alphabet identical to source UTM.
3. $\Gamma_R = \Gamma$: tape alphabet identical to source UTM.
4. $\delta_R : \mathcal{C}_R \to \mathcal{C}_R$: deterministic forward transition function acting on extended configurations.
5. $\delta_R^{-1} : \mathcal{C}_R \to \mathcal{C}_R$: deterministic reverse transition function acting on extended configurations.
6. $q_{\text{start}} \in Q_R$: initial control state.
7. $B = "\_" \in \Gamma_R$: blank symbol.
8. $q_{\text{halt}} \in Q_R$: halting state.

---

## 5. RUTM Configuration Model

### 5.1 Configuration Tuple

An extended RUTM configuration $C_R$ is defined as the 7-tuple:

$$C_R = (q, T, h, H, k, \text{halted}, \text{error})$$

where:
- $q \in Q$: current control state.
- $T : \mathbb{Z} \to \Gamma$: main tape memory function mapping integer tape positions to alphabet symbols.
- $h \in \mathbb{Z}$: main tape head position.
- $H \in \mathcal{H}$: auxiliary history log represented as a sequence of transition records:
  $$H = [r_1, r_2, \dots, r_k]$$
  where each record $r_i = (q_{i-1}, s_{i-1}, d_{i-1}) \in Q \times \Gamma \times \{L, R, S\}$ captures the exact predecessor state, overwritten symbol, and head movement direction.
- $k \in \mathbb{N}_0$: step counter ($k = |H|$).
- $\text{halted} \in \{\text{True}, \text{False}\}$: boolean halting flag.
- $\text{error} \in \text{Optional}[\text{str}]$: optional execution error message.

### 5.2 Initial Configuration

The initial RUTM configuration $C_{R,0}$ for an input tape $T_0$ is defined as:

$$C_{R,0} = (q_{\text{start}}, T_0, 0, [], 0, \text{False}, \text{None})$$

where $H_0 = []$ is the empty history sequence.

### 5.3 Configuration Equality

Two RUTM configurations $C_R^{(1)} = (q_1, T_1, h_1, H_1, k_1, \text{halt}_1, e_1)$ and $C_R^{(2)} = (q_2, T_2, h_2, H_2, k_2, \text{halt}_2, e_2)$ are equal ($C_R^{(1)} = C_R^{(2)}$) if and only if:
1. $q_1 = q_2$
2. $h_1 = h_2$
3. $k_1 = k_2$
4. $\text{halt}_1 = \text{halt}_2$
5. $e_1 = e_2$
6. $H_1 = H_2$ (exact sequence equality: $|H_1| = |H_2|$ and $\forall i, r_i^{(1)} = r_i^{(2)}$)
7. $\forall z \in \mathbb{Z}, T_1(z) = T_2(z)$ (main tape equality across all non-blank cells)

---

## 6. Forward Transition Relation ($R$)

The forward step transition function $R : \mathcal{C}_R \to \mathcal{C}_R$ executes as follows:

Given $C_R = (q, T, h, H, k, \text{halted}, \text{error})$:

1. **Halting & Error Guards:**
   - If $\text{halted} = \text{True}$ or $q = q_{\text{halt}}$, return $C_R$ (fixed point).
   - If $\text{error} \neq \text{None}$, return $C_R$.

2. **Read Symbol:**
   - Read current symbol $s = T(h)$.

3. **Transition Lookup:**
   - Lookup action $\delta(q, s) = (q', s', d)$ where $d \in \{L, R, S\}$.
   - If $\delta(q, s)$ is undefined, return $C'_R = (q, T, h, H, k, \text{False}, \text{"Undefined transition"})$.

4. **State & Memory Update:**
   - Construct new tape $T'$:
     $$T'(z) = \begin{cases} s' & \text{if } z = h \\ T(z) & \text{if } z \neq h \end{cases}$$
   - Construct new head position $h'$:
     $$h' = \begin{cases} h - 1 & \text{if } d = L \\ h + 1 & \text{if } d = R \\ h & \text{if } d = S \end{cases}$$

5. **History Record Construction:**
   - Construct history record $r = (q, s, d)$ recording predecessor state $q$, overwritten symbol $s$, and direction $d$.
   - Append to history log: $H' = H \mathbin{+\!\!+} [r]$.

6. **Return Configuration:**
   $$R(C_R) = (q', T', h', H', k+1, (q' == q_{\text{halt}}), \text{None})$$

---

## 7. Reverse Transition Relation ($R^{-1}$)

The inverse step transition function $R^{-1} : \mathcal{C}_R \to \mathcal{C}_R$ executes as follows:

Given $C'_R = (q', T', h', H', k', \text{halted}', \text{error}')$:

1. **Boundary Guards:**
   - If $k' = 0$ or $H' = []$, return $C'_R$ (cannot step backward past initial configuration).
   - If $\text{error}' \neq \text{None}$, return $C'_R$.

2. **Pop History Record:**
   - Decompose history sequence $H' = H \mathbin{+\!\!+} [r]$ where $r = (q, s, d)$.
   - The remaining history sequence is $H$.

3. **Invert Head Movement:**
   - Reconstruct predecessor head position $h$:
     $$h = \begin{cases} h' + 1 & \text{if } d = L \\ h' - 1 & \text{if } d = R \\ h' & \text{if } d = S \end{cases}$$

4. **Restore Overwritten Memory:**
   - Reconstruct predecessor main tape $T$:
     $$T(z) = \begin{cases} s & \text{if } z = h \\ T'(z) & \text{if } z \neq h \end{cases}$$

5. **Restore Control State:**
   - Restore predecessor control state $q$.

6. **Return Predecessor Configuration:**
   $$R^{-1}(C'_R) = (q, T, h, H, k'-1, \text{False}, \text{None})$$

---

## 8. Auxiliary / History Tracking Model ($H$)

### 8.1 Why History Tracking is Mathematically Mandatory

In standard classical Turing machines, transition functions $\delta : Q \times \Gamma \to Q \times \Gamma \times \{L, R, S\}$ are generally **non-injective** (many-to-one). Multiple distinct pairs $(q_1, s_1)$ and $(q_2, s_2)$ may transition to the same state $q'$ and write symbol $s'$. Consequently, given only the target state $q'$ and current tape $T'$, the predecessor configuration $(q, T, h)$ cannot be uniquely determined.

By appending the explicit predecessor record $r = (q, s, d)$ to an auxiliary history tape $H$, the extended configuration mapping $R : C_R \mapsto C'_R$ embeds the computation into an injective space.

### 8.2 Structure & Representation of History $H$

- $H$ is a pushdown sequence / history log of records $r_i = (q_{i-1}, s_{i-1}, d_{i-1})$.
- $H$ grows by exactly 1 record per forward step ($|H_k| = k$).
- $H$ shrinks by exactly 1 record per reverse step ($|H_{k-1}| = k-1$).
- Storage cost of $H$ after $k$ steps is $O(k)$ discrete history records.

---

## 9. Reversibility Definition & Classification

### 9.1 Mathematical Reversibility Condition

A transition relation $R$ on extended configuration domain $\text{Dom}(R) \subset \mathcal{C}_R$ is **logically and computationally reversible** if and only if there exists a deterministic computable function $R^{-1} : \text{Im}(R) \to \text{Dom}(R)$ such that:

$$\forall C_R \in \text{Dom}(R), \quad R^{-1}(R(C_R)) = C_R$$

and for any forward sequence $C_{R,0} \xrightarrow{R} C_{R,1} \xrightarrow{R} \dots \xrightarrow{R} C_{R,k}$:

$$\forall m \in \{1, \dots, k\}, \quad (R^{-1})^m(C_{R,k}) = C_{R,k-m}$$

### 9.2 Three Levels of Reversibility

Module 2 explicitly distinguishes three levels of reversibility:

1. **Logical Reversibility:** The state transition function $R$ is an injective mapping on configuration space, guaranteeing mathematical invertibility.
2. **Computational Reversibility:** The inverse mapping $R^{-1}$ is effectively computable in finite deterministic time per step.
3. **Thermodynamic Reversibility:** Physical dissipation-less computation (Landauer's principle $\Delta S = 0$).

> [!CAUTION]
> **CRITICAL SCIENTIFIC BOUNDARY:**  
> Module 2 establishes **Logical and Computational Reversibility**.  
> Module 2 does **NOT** claim Thermodynamic Reversibility or zero physical energy dissipation.  
> Storing history records $H$ avoids logical information loss during forward computation, but clearing or managing history physical memory in hardware is outside the computational model.

---

## 10. Invariants

### 10.1 Forward Execution Invariants

During forward execution $C_{R,0} \to C_{R,1} \to \dots \to C_{R,k}$:

1. **History Length Invariant:** $|H_k| = k = \text{step\_count}$.
2. **Projection Invariant:** $\pi_{\text{UTM}}(C_{R,k}) = C_k$, where $\pi_{\text{UTM}}(q, T, h, H, k, \text{halted}, \text{error}) = (q, T, h, k, \text{halted}, \text{error})$.
3. **Single-Step Invertibility Invariant:** $R^{-1}(R(C_{R,i})) = C_{R,i}$ for all $i \ge 0$.
4. **Tape Fidelity Invariant:** Main tape contents $T_k$ at cell $z$ are strictly identical between UTM and RUTM.

### 10.2 Reverse Execution Invariants

During reverse execution $(R^{-1})^m(C_{R,k})$ for $0 \le m \le k$:

1. **Trajectory Traceback Invariant:** $(R^{-1})^m(C_{R,k}) = C_{R,k-m}$.
2. **History Decrement Invariant:** $|H_{k-m}| = k - m$.
3. **Initial State Convergence:** $(R^{-1})^k(C_{R,k}) = C_{R,0} = (q_{\text{start}}, T_0, 0, [], 0, \text{False}, \text{None})$.

---

## 11. Semantic Preservation Boundary

Module 2 defines semantic preservation between source UTM and target RUTM via observable memory output functions:

$$\text{Obs}_{\text{UTM}}(C_{\text{final}}) \equiv \text{Obs}_{\text{RUTM}}(C_{R,\text{final}})$$

where $\text{Obs}_{\text{RUTM}}(C_R) = \text{Obs}_{\text{UTM}}(\pi_{\text{UTM}}(C_R))$.

### Scientific Claim Boundary:
- **Empirical Semantic Preservation:** Established for finite execution instances tested in Stage 9 & 10.
- **Universal Claim Boundary:** Certificate C2 will explicitly state `universal_claim = False` and `formal_proof = False` unless a machine-checked universal proof is constructed in Stage 4.

---

## 12. Proof Obligations for Stage 4

Stage 4 (Reversibility Construction & Proof) must satisfy the following explicit proof obligations:

1. **Lemma 1 (Left-Inverse Invariance):** Prove that for every valid $C_R \in \text{Dom}(R)$, $R^{-1}(R(C_R)) = C_R$.
2. **Lemma 2 (History Sequence Induction):** Prove by induction on step count $k$ that $(R^{-1})^k(R^k(C_{R,0})) = C_{R,0}$.
3. **Lemma 3 (Halting Preservation):** Prove that $C_{R,k}$ is in halting state $q_{\text{halt}}$ if and only if source UTM configuration $C_k$ is in $q_{\text{halt}}$.
4. **Lemma 4 (Observable Equivalence):** Prove that $\text{Obs}_{\text{RUTM}}(C_{R,\text{final}}) = \text{Obs}_{\text{UTM}}(C_{\text{final}})$.

---

## 13. Informational Efficiency & Overhead Metrics

Module 2 separates correctness from efficiency. The RUTM construction introduces explicit informational overheads that must be measured in Stage 11:

1. **History Space Overhead:** $\text{Space}_{\text{hist}}(k) = k \cdot (\log_2 |Q| + \log_2 |\Gamma| + 2)$ bits.
2. **Tape Cell Usage:** $\text{Cells}_{\text{RUTM}}(k) = \text{Cells}_{\text{UTM}}(k)$.
3. **Transition Step Overhead:** 1 forward RUTM step per 1 UTM step (1:1 step mapping in forward execution).
4. **Reverse Execution Time Cost:** 1 reverse RUTM step per 1 backward step (1:1 step mapping in reverse execution).

---

## 14. Non-Claims & Explicit Boundaries

1. **No Thermodynamic Claim:** The model does NOT claim zero energy dissipation or Landauer-limit physical reversibility.
2. **No Universal Theorem Claimed at Stage 1:** Empirical validation applies to finite test executions.
3. **No Modification of Module 1:** Module 1 source, tests, and Certificate C1 remain frozen and untouched.
4. **No Quantum Hardware Claim:** Quantum circuits, qubits, and QTM are deferred to Module 3 & 4.

---

## 15. Stage 2 Prerequisites

Before proceeding to **Stage 2 (RUTM Configuration Model)**:
1. Verify Stage 1 specification document internal consistency.
2. Verify all mathematical symbols and domain/codomain sets are fully defined.
3. Run frozen Module 1 test suite to confirm 100% regression pass (79/79 PASS).
4. Obtain explicit user authorization to advance to Stage 2.
