# Stage 3 Specification — RUTM Operational Semantics

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 3 — RUTM Operational Semantics  
**Status:** COMPLETE (FROZEN)  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`STAGE_1_RUTM_SPECIFICATION.md`](STAGE_1_RUTM_SPECIFICATION.md), [`STAGE_2_RUTM_CONFIGURATION.md`](STAGE_2_RUTM_CONFIGURATION.md)  

---

## 1. Purpose

The purpose of Stage 3 is to define the exact single-step forward transition relation $R : \mathcal{C}_R \times \text{UTMProgram} \to \mathcal{C}_R$ and single-step reverse transition relation $R^{-1} : \mathcal{C}_R \to \mathcal{C}_R$ for the Reversible Universal Turing Machine (RUTM).

Stage 3 establishes **HOW** a valid RUTM configuration $C_R$ is transformed atomically step-by-step, capturing history records prior to memory/state mutation, maintaining all Stage 2 representation invariants ($k = |H|$), preserving source UTM semantics under projection ($\pi_{\text{UTM}}$), and providing the operational foundation for the Stage 4 formal reversibility proof.

---

## 2. Scope

### In-Scope:
- Operational specification of single-step forward transition $R(C_R, \text{program}) \mapsto C'_R$.
- Operational specification of single-step reverse transition $R^{-1}(C'_R, [\text{program}]) \mapsto C_R$.
- History record capture order ($r = (q, s, d)$ recorded BEFORE mutation).
- Single-cell tape update semantics ($\forall z \neq h, T'(z) = T(z)$).
- Head movement ($\text{move\_head}$) and inverse movement ($\text{inverse\_move\_head}$).
- Step count increment ($k' = k + 1$) and decrement ($k = k' - 1$).
- Halting fixed-point boundary and error isolation semantics.
- Validation contract enforcement ($\text{Valid\_RUTM}(C_R)$ pre- and post-step).
- Projection correspondence $\pi_{\text{UTM}}(R(C_R)) = \delta(\pi_{\text{UTM}}(C_R))$.
- Implementation module `src/module2/rutm/semantics.py` and behavioral unit tests `tests/module2/test_stage3_rutm_semantics.py`.

### Out-of-Scope:
- Proving the universal reversibility theorem $R^{-1}(R(C_R)) = C_R$ (deferred to Stage 4).
- Multi-step execution simulator loop (Stage 7).
- Translator $T_2 : \text{UTM-IR} \to \text{RUTM-IR}$ (Stage 6).
- Thermodynamic zero-dissipation / physical energy claims.
- Modification of frozen Module 1 or Stage 2 configuration models.

---

## 3. Source UTM Transition Semantics

Stage 3 lifts the exact deterministic transition semantics of Module 1's frozen Universal Turing Machine ([`src/module1/utm/model.py`](../../src/module1/utm/model.py)):

$$\delta : (Q \setminus \{q_{\text{halt}}\}) \times \Gamma \longrightarrow Q \times \Gamma \times \{L, R, S\}$$

Given current UTM configuration $C = (q, T, h, k, \text{halted}, \text{error})$ and program $\text{UTMProgram}$:
1. Read current symbol $s = T(h)$.
2. Look up transition action:
   - Primary lookup: exact key $(q, s)$.
   - Wildcard fallback: key $(q, "\_")$ (preserving $s$ if `write_symbol == "_"`).
3. If action $\delta(q, s) = (q', s', d)$ exists:
   - Write $T'[h] = s'$ and keep all $z \neq h$ unchanged ($T'[z] = T(z)$).
   - Move head $h' = \text{move}(h, d)$.
   - Update state $q \to q'$.
   - Increment step counter $k \to k + 1$.
   - Set $\text{halted} = (q' == q_{\text{halt}})$.
4. If transition is undefined:
   - Set $\text{error} = \text{"Undefined transition..."}$ without mutating tape, head, or step count.

---

## 4. RUTM Forward Transition Semantics ($R$)

### 4.1 Signature & Function Definition
$$R : \mathcal{C}_R \times \text{UTMProgram} \longrightarrow \mathcal{C}_R$$

Given $C_R = (q, T, h, H, k, \text{halted}, \text{error})$ and program $P$:

### 4.2 Order of Operational Steps

```
[Input C_R] ──► 1. Pre-validation ──► 2. Halt/Error Check ──► 3. Read T(h)
                                                                 │
[Output C'_R] ◄── 8. Return C'_R ◄── 7. Update State/k ◄── 6. Push H ◄── 5. Mutate Tape/Head
```

1. **Pre-Step Validation:**
   Assert $\text{Valid\_RUTM}(C_R) = \text{True}$ against program context. If invalid, return copy of $C_R$ with `error="Invalid input configuration..."`.
2. **Terminal / Fixed-Point Check:**
   If $\text{halted} = \text{True}$ or $q = q_{\text{halt}}$, return $C_R$ unchanged.
   If $\text{error} \neq \text{None}$, return $C_R$ unchanged.
3. **Read Symbol:**
   $s = T(h) = \text{Read}(T, h)$.
4. **Transition Lookup:**
   Look up action $\delta(q, s) = (q', s', d)$ where $d \in \{L, R, S\}$.
   If $\delta(q, s)$ is undefined:
   Return $C'_R = (q, T, h, H, k, \text{False}, \text{"Undefined transition for state 'q' and symbol 's'"})$.
   *(Atomic property: tape, head, history, step count are preserved un-mutated).*
5. **History Record Capture (BEFORE Mutation):**
   Construct predecessor record:
   $$r = (q, s, d) \in Q \times \Gamma \times \{L, R, S\}$$
   where $q$ is exact predecessor state, $s$ is exact read symbol prior to overwrite, and $d$ is head movement direction.
6. **Main Tape Mutation:**
   Construct updated tape $T'$:
   $$T'(z) = \begin{cases} s' & \text{if } z = h \\ T(z) & \text{if } z \neq h \end{cases}$$
7. **Head Movement Update:**
   $$h' = \text{move\_head}(h, d) = \begin{cases} h - 1 & \text{if } d = L \\ h + 1 & \text{if } d = R \\ h & \text{if } d = S \end{cases}$$
8. **History Log Update:**
   $$H' = \text{push\_history}(H, r) = H \mathbin{+\!\!+} [(q, s, d)]$$
9. **Step Counter Update:**
   $$k' = k + 1$$
10. **Halting & Return:**
    $$\text{halted}' = (q' == q_{\text{halt}})$$
    $$R(C_R, P) = (q', T', h', H', k+1, \text{halted}', \text{None})$$

---

## 5. History Capture Semantics

History capture is the core operational difference between standard UTM and RUTM:

- **Pre-Mutation Requirement:** Record $r = (q, s, d)$ MUST be constructed BEFORE $T[h]$ is overwritten by $s'$ and BEFORE $q$ is updated to $q'$.
- **Fidelity:** $s$ captures the exact pre-transition symbol (whether non-blank or blank $"\_"$).
- **Invariance:** $|H'| = |H| + 1 = k + 1$, maintaining representation invariant $k' = |H'|$.

---

## 6. Tape, Head, State, and Step-Count Updates

- **Tape Update:** Operates on single cell $h$. All non-head cells $z \neq h$ are strictly preserved ($\forall z \neq h, T'(z) = T(z)$).
- **Head Update:** Operates via frozen Stage 2 `move_head(h, d)`.
- **State Update:** Advances control state from predecessor $q$ to successor $q'$.
- **Step-Count Update:** Strictly increments step counter $k \to k + 1$.

---

## 7. Halt and Error Operational Semantics

### 7.1 Halt Semantics
- When transition target $q' = q_{\text{halt}}$, $C'_R$ has $q' = q_{\text{halt}}$ and $\text{halted}' = \text{True}$.
- Subsequent forward calls $R(C'_R)$ hit the fixed-point guard and return $C'_R$ unchanged.
- The history log $H'$ contains all step records up to halting, allowing reverse steps $R^{-1}$ out of $q_{\text{halt}}$.

### 7.2 Error Semantics
- Undefined transition $\delta(q, s) = \text{None}$ creates an error configuration $C_{\text{err}}$ with `error="Undefined transition..."`.
- $C_{\text{err}}$ preserves $H, k, T, h, q$ without partial state corruption.
- Error configurations are non-reversible and return $C_{\text{err}}$ under subsequent $R$ or $R^{-1}$ calls.

---

## 8. Configuration Validity Contract

For any forward step $C'_R = R(C_R, P)$:
$$\text{Valid\_RUTM}(C_R) \land (\delta(q, T(h)) \neq \text{None}) \implies \text{Valid\_RUTM}(C'_R)$$

The forward step preserves all representation invariants:
- $k' = |H'| = k + 1$
- $\text{halted}' = \text{True} \iff q' = q_{\text{halt}}$
- $h' \in \mathbb{Z}$
- $T'(z) \in \Gamma$

---

## 9. Reverse Operational Contract ($R^{-1}$)

### 9.1 Signature & Function Definition
$$R^{-1} : \mathcal{C}_R \times \text{Optional}[\text{UTMProgram}] \longrightarrow \mathcal{C}_R$$

Given $C'_R = (q', T', h', H', k', \text{halted}', \text{error}')$ and optional program context $P$:

### 9.2 Order of Reverse Operational Steps

1. **Pre-Step Validation:**
   Assert $\text{Valid\_RUTM}(C'_R) = \text{True}$ against program context (when $P$ is provided) or structural context (when $P$ is omitted). If invalid, return copy with `error="Invalid configuration for reverse step: {err}"`.
2. **Boundary & Error Checks:**
   If $\text{error}' \neq \text{None}$, return $C'_R$ unchanged.
   If $k' = 0$ or $H' = []$, return copy of $C'_R$ with `error="Cannot reverse initial configuration (history is empty)"`.
3. **Pop History Record:**
   $(H, r) = \text{pop\_history}(H')$ where $r = (q, s, d)$.
4. **Inverse Head Movement:**
   $$h = \text{inverse\_move\_head}(h', d) = \begin{cases} h' + 1 & \text{if } d = L \\ h' - 1 & \text{if } d = R \\ h' & \text{if } d = S \end{cases}$$
5. **Restore Overwritten Tape Symbol:**
   Construct predecessor tape $T$:
   $$T(z) = \begin{cases} s & \text{if } z = h \\ T'(z) & \text{if } z \neq h \end{cases}$$
6. **Restore Predecessor Control State:**
   $q = r.\text{prev\_state}$.
7. **Decrement Step Counter:**
   $$k = k' - 1$$
8. **Halting & Return:**
   $$\text{halted} = (q == \text{halt\_state})$$
   $$R^{-1}(C'_R, P) = (q, T, h, H, k'-1, \text{halted}, \text{None})$$

---

## 10. Projection Correspondence ($\pi_{\text{UTM}}$)

The projection function $\pi_{\text{UTM}} : \mathcal{C}_R \to \mathcal{C}_{\text{UTM}}$ expresses the intended single-step operational correspondence:

$$\forall C_R \in \text{Dom}(R_{\text{rev}}), \quad \pi_{\text{UTM}}(R(C_R, P)) = \text{step\_utm\_configuration}(\pi_{\text{UTM}}(C_R), P)$$

> [!IMPORTANT]
> **CLAIM BOUNDARY:**  
> The equation above is an **intended mathematical operational correspondence and Stage 4 proof obligation**.  
> The current Stage 3 unit test suite provides **empirical single-step differential correspondence verification** for representative test cases.  
> Machine-checked universal proof of projection preservation ($\pi_{\text{UTM}} \circ R = \delta \circ \pi_{\text{UTM}}$) is explicitly deferred to Stage 4.

---

## 11. Core Operational Invariants

During execution of $R$ and $R^{-1}$:
1. **$I_1$ (Counter-History Invariant):** $k' = |H'|$ holds at every forward and reverse step.
2. **$I_2$ (Single-Cell Mutation Invariant):** $\forall z \neq h, T'(z) = T(z)$.
3. **$I_3$ (Atomic Error Preservation Invariant):** Undefined transitions set `error` string without modifying tape, head, or history.
4. **$I_4$ (Halting Consistency Invariant):** $\text{halted} = \text{True} \iff q = q_{\text{halt}}$ at all steps.

---

## 12. Proof Obligations Formulated for Stage 4

Stage 3 formulates the operational statements required for Stage 4 formal proof:
1. **$P_1$ (Single-Step Inverse Property):** Formulate $\forall C_R \in \text{Dom}(R_{\text{rev}}), R^{-1}(R(C_R, P), P) = C_R$.
2. **$P_2$ (Commutative Diagram Statement):** Formulate $\pi_{\text{UTM}}(R(C_R, P)) = \delta(\pi_{\text{UTM}}(C_R), P)$.
3. **$P_3$ (Traceback Convergence):** Formulate $(R^{-1})^k(R^k(C_{R,0}, P), P) = C_{R,0}$.

---

## 13. Non-Claims & Explicit Boundaries

1. **No Universal Theorem Claimed at Stage 3:** Passing empirical differential tests verifies operational correspondence for test instances; universal mathematical proofs belong to Stage 4.
2. **No Thermodynamic Reversibility Claim:** History tracking establishes logical/computational operational reversibility, not physical zero energy dissipation.
3. **No Modification of Module 1 or Stage 2:** All code additions are strictly isolated in Stage 3 module `src/module2/rutm/semantics.py`.

---

## 14. Stage 4 Prerequisites

Before proceeding to **Stage 4 (Reversibility Construction & Proof)**:
1. Verify `src/module2/rutm/semantics.py` passes all Stage 3 operational tests.
2. Verify frozen Module 1 regression test suite (79/79 PASS).
3. Obtain explicit user authorization to advance to Stage 4.
