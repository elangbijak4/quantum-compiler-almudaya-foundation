# Stage 4 Formal Proof — RUTM Reversibility Construction & Proof

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 4 — Formal RUTM Reversibility Construction and Proof  
**Status:** COMPLETE  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`STAGE_1_RUTM_SPECIFICATION.md`](STAGE_1_RUTM_SPECIFICATION.md), [`STAGE_2_RUTM_CONFIGURATION.md`](STAGE_2_RUTM_CONFIGURATION.md), [`STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md)  
**Implementation Modules:** [`src/module2/rutm/model.py`](../../src/module2/rutm/model.py), [`src/module2/rutm/semantics.py`](../../src/module2/rutm/semantics.py)  

---

## 1. Executive Summary

Stage 4 establishes the formal mathematical proofs of reversibility and projection preservation for the Reversible Universal Turing Machine (RUTM) model defined in Module 2.

This document contains explicit component-wise proofs for:
1. **Lemma 1 (Head Movement Inversion Identity):** $\forall h \in \mathbb{Z}, \forall d \in \{L, R, S\}, \text{inverse\_move}(\text{move}(h, d), d) = h$.
2. **Lemma 2 (History Sequence Decomposition):** $\text{pop}(\text{push}(H, r)) = (H, r)$.
3. **Lemma 3 (Tape Extensional Restoration):** $\forall z \in \mathbb{Z}, T_{\text{rev}}(z) = T(z)$.
4. **Lemma 4 (Counter & Invariant Preservation):** $k_{\text{rev}} = k$ and $|H_{\text{rev}}| = k_{\text{rev}}$.
5. **Lemma 5 (Halting & Error Invariant Preservation):** $\text{halted}_{\text{rev}} = \text{halted}$ and $\text{error}_{\text{rev}} = \text{None}$.
6. **Theorem 1 (Single-Step Reversibility):** $\forall C_R \in \text{Dom}_{\text{rev}}(P), R^{-1}(R(C_R, P), P) = C_R$.
7. **Corollary 1 (Local Inverse Identity):** $R_P^{-1} \circ R_P = \text{id}_{\text{Dom}_{\text{rev}}(P)}$.
8. **Theorem 2 (Finite-Trace Reversibility):** Proof by mathematical induction that $(R_P^{-1})^n(R_P^n(C_{R,0})) = C_{R,0}$.
9. **Theorem 3 (Projection Preservation & Commuting Diagram):** Component-wise proof that $\pi_{\text{UTM}} \circ R = \delta \circ \pi_{\text{UTM}}$.

---

## 2. Definitions & Formal Reversible Domain

### Definition 1 (Extended RUTM Configuration)
An extended RUTM configuration $C_R$ is the 7-tuple:
$$C_R = (q, T, h, H, k, \text{halted}, \text{error})$$
where $q \in Q$, $T : \mathbb{Z} \to \Gamma$, $h \in \mathbb{Z}$, $H = [r_1, \dots, r_k]$ with $r_i = (q_{i-1}, s_{i-1}, d_{i-1}) \in Q \times \Gamma \times \{L, R, S\}$, $k \in \mathbb{N}_0$, $\text{halted} \in \{\text{True}, \text{False}\}$, and $\text{error} \in \text{Optional}[\text{str}]$.

### Definition 2 (Valid Configuration Predicate $\text{Valid\_RUTM}(C_R)$)
A configuration $C_R$ is valid ($\text{Valid\_RUTM}(C_R) = \text{True}$) if and only if:
1. $q \in Q$ (non-empty string state identifier).
2. $h \in \mathbb{Z}$ (integer head coordinate).
3. $k \in \mathbb{N}_0$ (non-negative step count integer).
4. Representation Invariant: $k = |H|$.
5. Halting Consistency Invariant: $\text{halted} = \text{True} \iff q = q_{\text{halt}}$.
6. Tape domain: $\forall z \in \mathbb{Z}, T(z) \in \Gamma$.
7. History record integrity: $\forall (q_i, s_i, d_i) \in H, q_i \in Q \land s_i \in \Gamma \land d_i \in \{L, R, S\}$.

### Definition 3 (Formal Reversible Execution Domain $\text{Dom}_{\text{rev}}(P)$)
For a deterministic program $P = (Q, \Sigma, \Gamma, \delta, q_{\text{start}}, B, q_{\text{halt}})$, the formal reversible execution domain $\text{Dom}_{\text{rev}}(P) \subset \mathcal{C}_R$ is defined as:
$$\text{Dom}_{\text{rev}}(P) = \{ C_R \in \mathcal{C}_R \mid \text{Valid\_RUTM}(C_R) = \text{True} \land \text{error} = \text{None} \land \text{halted} = \text{False} \land \exists \delta(q, T(h)) \}$$

---

## 3. Recaps of Operational Semantics

### 3.1 Forward Step Relation $R(C_R, P)$
For $C_R = (q, T, h, H, k, \text{False}, \text{None}) \in \text{Dom}_{\text{rev}}(P)$ with $\delta(q, T(h)) = (q', s', d)$:
1. Read $s = T(h)$.
2. Record $r = (q, s, d)$.
3. Tape $T'(z) = \begin{cases} s' & \text{if } z = h \\ T(z) & \text{if } z \neq h \end{cases}$
4. Head $h' = \text{move}(h, d) = \begin{cases} h - 1 & \text{if } d = L \\ h + 1 & \text{if } d = R \\ h & \text{if } d = S \end{cases}$
5. History $H' = H \mathbin{+\!\!+} [r]$.
6. Step counter $k' = k + 1$.
7. Halted flag $\text{halted}' = (q' == q_{\text{halt}})$.
8. Result: $C'_R = R(C_R, P) = (q', T', h', H', k', \text{halted}', \text{None})$.

### 3.2 Reverse Step Relation $R^{-1}(C'_R, P)$
For $C'_R = (q', T', h', H', k', \text{halted}', \text{None}) \in \text{Im}(R_P)$ with $k' > 0$ and $H' \neq []$:
1. Pop $(H, r) = \text{pop}(H')$ where $r = (q_{\text{prev}}, s_{\text{overwritten}}, d_{\text{prev}})$.
2. Head $h_{\text{rev}} = \text{inverse\_move}(h', d_{\text{prev}}) = \begin{cases} h' + 1 & \text{if } d_{\text{prev}} = L \\ h' - 1 & \text{if } d_{\text{prev}} = R \\ h' & \text{if } d_{\text{prev}} = S \end{cases}$
3. Tape $T_{\text{rev}}(z) = \begin{cases} s_{\text{overwritten}} & \text{if } z = h_{\text{rev}} \\ T'(z) & \text{if } z \neq h_{\text{rev}} \end{cases}$
4. State $q_{\text{rev}} = q_{\text{prev}}$.
5. Step counter $k_{\text{rev}} = k' - 1$.
6. Halted flag $\text{halted}_{\text{rev}} = (q_{\text{rev}} == q_{\text{halt}})$.
7. Result: $R^{-1}(C'_R, P) = (q_{\text{rev}}, T_{\text{rev}}, h_{\text{rev}}, H, k_{\text{rev}}, \text{halted}_{\text{rev}}, \text{None})$.

---

## 4. Fundamental Inversion Lemmas

### Lemma 1 (Head Movement Inversion Identity)
For all $h \in \mathbb{Z}$ and all directions $d \in \{L, R, S\}$:
$$\text{inverse\_move}(\text{move}(h, d), d) = h$$

**Proof:** We proceed by case analysis on $d \in \{L, R, S\}$:
- **Case 1 ($d = L$):**  
  $\text{move}(h, L) = h - 1$.  
  $\text{inverse\_move}(h - 1, L) = (h - 1) + 1 = h$.
- **Case 2 ($d = R$):**  
  $\text{move}(h, R) = h + 1$.  
  $\text{inverse\_move}(h + 1, R) = (h + 1) - 1 = h$.
- **Case 3 ($d = S$):**  
  $\text{move}(h, S) = h$.  
  $\text{inverse\_move}(h, S) = h$.

In all three cases, $\text{inverse\_move}(\text{move}(h, d), d) = h$. $\blacksquare$

---

### Lemma 2 (History Sequence Push/Pop Inversion)
For any history sequence $H \in \mathcal{H}$ and record $r \in \text{Record}$:
$$\text{pop}(\text{push}(H, r)) = (H, r)$$

**Proof:**  
By definition, $\text{push}(H, r) = H \mathbin{+\!\!+} [r]$.  
By definition of sequence decomposition on $H' = H \mathbin{+\!\!+} [r]$, $\text{pop}(H') = (H'[:-1], H'[-1])$.  
Since $H'[:-1] = H$ and $H'[-1] = r$, $\text{pop}(\text{push}(H, r)) = (H, r)$.  
Furthermore, $|\text{push}(H, r)| = |H| + 1$, and $|\text{pop}(H')_1| = |H'| - 1 = (|H| + 1) - 1 = |H|$. $\blacksquare$

---

### Lemma 3 (Tape Extensional Restoration)
Let $C_R = (q, T, h, H, k, \text{halted}, \text{None}) \in \text{Dom}_{\text{rev}}(P)$ with read symbol $s = T(h)$, write symbol $s'$, and direction $d$. Let $C'_R = R(C_R, P)$ and $C_{\text{rev}} = R^{-1}(C'_R, P)$. Then:
$$\forall z \in \mathbb{Z}, \quad T_{\text{rev}}(z) = T(z)$$

**Proof:**  
From Lemma 1, the restored head position is $h_{\text{rev}} = h$.  
From Lemma 2, the popped history record is $r = (q, s, d)$, so $s_{\text{overwritten}} = s = T(h)$.  
The reverse tape update sets $T_{\text{rev}}$ as:
$$T_{\text{rev}}(z) = \begin{cases} s_{\text{overwritten}} & \text{if } z = h_{\text{rev}} \\ T'(z) & \text{if } z \neq h_{\text{rev}} \end{cases} = \begin{cases} s & \text{if } z = h \\ T'(z) & \text{if } z \neq h \end{cases}$$

Now consider any arbitrary cell coordinate $z \in \mathbb{Z}$:
- **Subcase 1 ($z = h$):**  
  $T_{\text{rev}}(h) = s = T(h)$. Thus $T_{\text{rev}}(h) = T(h)$.
- **Subcase 2 ($z \neq h$):**  
  By forward step definition, $T'(z) = T(z)$ for $z \neq h$.  
  By reverse step definition, $T_{\text{rev}}(z) = T'(z)$ for $z \neq h$.  
  Therefore, $T_{\text{rev}}(z) = T(z)$.

Since $T_{\text{rev}}(z) = T(z)$ for all $z \in \mathbb{Z}$, the functions $T_{\text{rev}}$ and $T$ are extensionally equal ($T_{\text{rev}} = T$). $\blacksquare$

---

### Lemma 4 (Step Counter & History Invariant Preservation)
Let $C_R \in \text{Dom}_{\text{rev}}(P)$ with counter $k$ and history $H$ where $|H| = k$. Let $C'_R = R(C_R, P)$ and $C_{\text{rev}} = R^{-1}(C'_R, P)$. Then:
$$k_{\text{rev}} = k \quad \text{and} \quad |H_{\text{rev}}| = k_{\text{rev}}$$

**Proof:**  
In forward step: $k' = k + 1$ and $H' = H \mathbin{+\!\!+} [r]$, so $|H'| = |H| + 1 = k + 1 = k'$.  
In reverse step: $k_{\text{rev}} = k' - 1 = (k + 1) - 1 = k$.  
From Lemma 2: $H_{\text{rev}} = H$, so $|H_{\text{rev}}| = |H| = k = k_{\text{rev}}$.  
Thus $k_{\text{rev}} = k$ and the representation invariant $|H_{\text{rev}}| = k_{\text{rev}}$ holds. $\blacksquare$

---

### Lemma 5 (Halting & Error State Invariant Restoration)
Let $C_R = (q, T, h, H, k, \text{halted}, \text{None}) \in \text{Dom}_{\text{rev}}(P)$. Let $C'_R = R(C_R, P)$ and $C_{\text{rev}} = R^{-1}(C'_R, P)$. Then:
$$\text{halted}_{\text{rev}} = \text{halted} \quad \text{and} \quad \text{error}_{\text{rev}} = \text{None}$$

**Proof:**  
From Lemma 2, the popped history record contains $r.\text{prev\_state} = q$.  
Reverse state restoration sets $q_{\text{rev}} = r.\text{prev\_state} = q$.  
Since $C_R \in \text{Dom}_{\text{rev}}(P)$, $C_R$ satisfies halting consistency: $\text{halted} = \text{True} \iff q = q_{\text{halt}}$.  
The reverse step computes $\text{halted}_{\text{rev}} = (q_{\text{rev}} == q_{\text{halt}}) = (q == q_{\text{halt}}) = \text{halted}$.  
The reverse step on non-error $C'_R$ sets $\text{error}_{\text{rev}} = \text{None} = \text{error}$. $\blacksquare$

---

## 5. Main Single-Step Reversibility Theorem

### Theorem 1 (Single-Step Reversibility)
For any deterministic program $P$ and any extended configuration $C_R \in \text{Dom}_{\text{rev}}(P)$:

$$R^{-1}(R(C_R, P), P) = C_R$$

**Proof:**  
Let $C_R = (q, T, h, H, k, \text{halted}, \text{error}) \in \text{Dom}_{\text{rev}}(P)$.  
Let $C'_R = R(C_R, P) = (q', T', h', H', k', \text{halted}', \text{error}')$.  
Let $C_{\text{rev}} = R^{-1}(C'_R, P) = (q_{\text{rev}}, T_{\text{rev}}, h_{\text{rev}}, H_{\text{rev}}, k_{\text{rev}}, \text{halted}_{\text{rev}}, \text{error}_{\text{rev}})$.

We prove configuration tuple equality $C_{\text{rev}} = C_R$ by proving equality across all seven components:

1. **State Component ($q_{\text{rev}} = q$):**  
   $q_{\text{rev}} = r.\text{prev\_state} = q$ (by Lemma 5).
2. **Tape Component ($T_{\text{rev}} = T$):**  
   $\forall z \in \mathbb{Z}, T_{\text{rev}}(z) = T(z)$ (by Lemma 3).
3. **Head Component ($h_{\text{rev}} = h$):**  
   $h_{\text{rev}} = \text{inverse\_move}(\text{move}(h, d), d) = h$ (by Lemma 1).
4. **History Component ($H_{\text{rev}} = H$):**  
   $H_{\text{rev}} = \text{pop}(\text{push}(H, r))_1 = H$ (by Lemma 2).
5. **Step Counter Component ($k_{\text{rev}} = k$):**  
   $k_{\text{rev}} = (k + 1) - 1 = k$ (by Lemma 4).
6. **Halted Component ($\text{halted}_{\text{rev}} = \text{halted}$):**  
   $\text{halted}_{\text{rev}} = (q == q_{\text{halt}}) = \text{halted}$ (by Lemma 5).
7. **Error Component ($\text{error}_{\text{rev}} = \text{error}$):**  
   $\text{error}_{\text{rev}} = \text{None} = \text{error}$ (by Lemma 5).

Since all seven components are identical, $C_{\text{rev}} = C_R$, proving $R^{-1}(R(C_R, P), P) = C_R$. $\blacksquare$

---

### Corollary 1 (Local Inverse Identity)
The reverse transition operator $R_P^{-1}$ is the exact left-inverse of the forward transition operator $R_P$ on the domain $\text{Dom}_{\text{rev}}(P)$:

$$R_P^{-1} \circ R_P = \text{id}_{\text{Dom}_{\text{rev}}(P)}$$

**Proof:** Direct consequence of Theorem 1. $\blacksquare$

---

## 6. Main Finite-Trace Reversibility Theorem

### Theorem 2 (Finite-Trace Reversibility)
Let $P$ be a deterministic program. Let $C_{R,0} \in \text{Dom}_{\text{rev}}(P)$ be an initial RUTM configuration. Suppose forward execution generates a trace of length $n \in \mathbb{N}_0$:
$$C_{R,0} \xrightarrow{R_P} C_{R,1} \xrightarrow{R_P} C_{R,2} \xrightarrow{R_P} \dots \xrightarrow{R_P} C_{R,n}$$
such that every intermediate configuration $C_{R,i} \in \text{Dom}_{\text{rev}}(P)$ for $0 \le i < n$. Then:

$$(R_P^{-1})^n(R_P^n(C_{R,0})) = C_{R,0}$$

**Proof:**  
We proceed by mathematical induction on trace length $n \in \mathbb{N}_0$.

- **Base Case ($n = 0$):**  
  For $n = 0$, $R_P^0(C_{R,0}) = C_{R,0}$ and $(R_P^{-1})^0(C_{R,0}) = C_{R,0}$.  
  Thus $(R_P^{-1})^0(R_P^0(C_{R,0})) = C_{R,0}$. The base case holds.

- **Inductive Hypothesis ($n = m$):**  
  Assume that for any trace of length $m \ge 0$, $(R_P^{-1})^m(R_P^m(C_{R,0})) = C_{R,0}$.

- **Inductive Step ($n = m + 1$):**  
  Consider a trace of length $m + 1$:  
  $R_P^{m+1}(C_{R,0}) = R_P(R_P^m(C_{R,0})) = R_P(C_{R,m}) = C_{R,m+1}$.  
  Applying $(R_P^{-1})^{m+1}$ to $C_{R,m+1}$:
  $$(R_P^{-1})^{m+1}(R_P^{m+1}(C_{R,0})) = (R_P^{-1})^m \left( R_P^{-1} \left( R_P(C_{R,m}) \right) \right)$$
  
  Since $C_{R,m} \in \text{Dom}_{\text{rev}}(P)$, we apply Theorem 1 to the innermost term:
  $$R_P^{-1}(R_P(C_{R,m})) = C_{R,m}$$
  
  Substituting this back into the expression yields:
  $$(R_P^{-1})^m \left( C_{R,m} \right) = (R_P^{-1})^m \left( R_P^m(C_{R,0}) \right)$$
  
  By the Inductive Hypothesis, $(R_P^{-1})^m(R_P^m(C_{R,0})) = C_{R,0}$.  
  Therefore, $(R_P^{-1})^{m+1}(R_P^{m+1}(C_{R,0})) = C_{R,0}$.

By the principle of mathematical induction, Theorem 2 holds for all $n \in \mathbb{N}_0$. $\blacksquare$

---

## 7. Projection Preservation & Commuting Diagram Theorem

### Theorem 3 (Projection Preservation & Commuting Diagram)
Let $\pi_{\text{UTM}} : \mathcal{C}_R \to \mathcal{C}_{\text{UTM}}$ be the canonical projection function $\pi_{\text{UTM}}(q, T, h, H, k, \text{halted}, \text{error}) = (q, T, h, k, \text{halted}, \text{error})$.  
For any $C_R \in \text{Dom}_{\text{rev}}(P)$:

$$\pi_{\text{UTM}}(R(C_R, P)) = \text{step\_utm\_configuration}(\pi_{\text{UTM}}(C_R), P)$$

Equivalently, the following diagram commutes:

```
                         R_P
        C_R  ----------------------> C'_R
         |                              |
  π_UTM  |                              | π_UTM
         ▼                              ▼
        C   ---------------------->  C'
                         δ_P
```

**Proof:**  
Let $C_R = (q, T, h, H, k, \text{False}, \text{None}) \in \text{Dom}_{\text{rev}}(P)$.  
Then $\pi_{\text{UTM}}(C_R) = (q, T, h, k, \text{False}, \text{None}) = C_{\text{UTM}}$.

Now evaluate $\text{step\_utm\_configuration}(C_{\text{UTM}}, P)$:
1. Read symbol $s = C_{\text{UTM}}.\text{get\_tape\_symbol}() = T(h)$.
2. Lookup action $\delta(q, s) = (q', s', d)$.
3. Target tape $T_{\text{UTM}}'(z) = \begin{cases} s' & \text{if } z = h \\ T(z) & \text{if } z \neq h \end{cases}$.
4. Target head $h_{\text{UTM}}' = \text{move}(h, d)$.
5. Target step count $k_{\text{UTM}}' = k + 1$.
6. Target halted flag $\text{halted}_{\text{UTM}}' = (q' == q_{\text{halt}})$.
7. $C_{\text{UTM}}' = (q', T_{\text{UTM}}', h_{\text{UTM}}', k+1, \text{halted}_{\text{UTM}}', \text{None})$.

Now evaluate $\pi_{\text{UTM}}(R(C_R, P))$:
From Section 3.1, $R(C_R, P) = (q', T', h', H', k+1, \text{halted}', \text{None})$ where:
- $T' = T_{\text{UTM}}'$
- $h' = h_{\text{UTM}}'$
- $\text{halted}' = \text{halted}_{\text{UTM}}'$

Applying $\pi_{\text{UTM}}$:
$$\pi_{\text{UTM}}(R(C_R, P)) = (q', T', h', k+1, \text{halted}', \text{None}) = C_{\text{UTM}}'$$

Thus $\pi_{\text{UTM}}(R(C_R, P)) = \text{step\_utm\_configuration}(\pi_{\text{UTM}}(C_R), P)$. The diagram commutes. $\blacksquare$

---

## 8. Critical Distinction Between Theorems

> [!IMPORTANT]
> **LOGICAL SEPARATION OF THEOREMS:**  
> 1. **Logical Reversibility (Theorem 1 & 2):** $R_P^{-1} \circ R_P = \text{id}$. Proves that forward execution trajectory $C_{R,0} \to \dots \to C_{R,n}$ can be perfectly inverted backward step-by-step to recover the exact initial configuration $C_{R,0}$.
> 2. **Semantic Preservation (Theorem 3):** $\pi_{\text{UTM}} \circ R_P = \delta_P \circ \pi_{\text{UTM}}$. Proves that the projected computational state of RUTM tracks the exact execution state of the source UTM.
> 
> These two theorems are logically independent. Neither implies the other. Both have been proven component-wise.

---

## 9. Non-Claims & Explicit Boundaries

1. **No Thermodynamic Reversibility Claim:** Theorem 1 proves logical/computational invertibility ($R^{-1} \circ R = \text{id}$). It does NOT claim physical Landauer zero-energy dissipation ($\Delta S = 0$).
2. **No Quantum Hardware Claim:** QTM, QUTM, and quantum gate compilations belong to Module 3 & 4.
3. **No Modification of Frozen Predessors:** Module 1 source code, Stage 2 configuration models, and Stage 3 operational semantics remain 100% frozen and untouched.

---

## 10. Stage 5 Prerequisites

Before proceeding to **Stage 5 (RUTM-IR Model)**:
1. Verify Stage 4 proof documentation is internally consistent.
2. Verify empirical test suite `tests/module2/test_stage4_reversibility.py` passes 100%.
3. Verify frozen Module 1 regression suite (79/79 PASS) and Module 2 suite (39/39 PASS).
4. Obtain explicit user authorization to advance to Stage 5.
