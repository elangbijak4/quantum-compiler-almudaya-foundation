# Stage 6 Specification — UTM-IR $\to$ RUTM-IR Translation

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 6 — UTM-IR $\to$ RUTM-IR Translator  
**Status:** COMPLETE  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`STAGE_1_RUTM_SPECIFICATION.md`](STAGE_1_RUTM_SPECIFICATION.md), [`STAGE_2_RUTM_CONFIGURATION.md`](STAGE_2_RUTM_CONFIGURATION.md), [`STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md), [`STAGE_4_RUTM_REVERSIBILITY_PROOF.md`](STAGE_4_RUTM_REVERSIBILITY_PROOF.md), [`STAGE_5_RUTM_IR.md`](STAGE_5_RUTM_IR.md)  
**Implementation Package:** [`src/module2/translation/`](../../src/module2/translation)  

---

## 1. Purpose

The purpose of Stage 6 is to construct the formal translator $T_{UR} : \text{UTM-IR} \to \text{RUTM-IR}$ that converts any valid classical Universal Turing Machine description (`UTMProgram`) into a valid Reversible Universal Turing Machine description (`RUTM_IR`) conforming to the RUTM construction defined and formally proven in Stages 1–4.

$$\text{UTM-IR (Module 1)} \xrightarrow{\quad T_{UR} \quad} \text{RUTM-IR (Stage 5)} \xrightarrow{\quad \pi_{\text{UTM}} \circ R_P \quad} \text{Reversible Execution (Stages 3--4)}$$

---

## 2. Source and Target Domains

- **Source Domain ($\text{UTM-IR}_{\text{valid}}$):** Set of valid `UTMProgram` instances satisfying `validate_utm_program(program) == (True, None)`.
- **Target Domain ($\text{RUTM-IR}_{\text{valid}}$):** Set of valid `RUTM_IR` instances satisfying `validate_rutm_ir(rutm_ir) == (True, None)`.
- **Contract A (Validity Preservation):**  
  $$\forall U \in \text{UTM-IR}_{\text{valid}}, \quad T_{UR}(U) \in \text{RUTM-IR}_{\text{valid}}$$

---

## 3. Formal Translation Function $T_{UR}$

Given a source machine $U = (Q_U, \Sigma_U, \Gamma_U, B_U, q_{\text{start},U}, q_{\text{halt},U}, \delta_U)$:

$$T_{UR}(U) = (\text{name}, Q_R, \Sigma_R, \Gamma_R, B_R, q_{\text{start},R}, q_{\text{halt},R}, \delta_R, \text{HistoryPolicy}_R, \text{Provenance}_R)$$

### 3.1 Component Mappings:
1. `name` $= \text{machine\_name} \lor \text{"RUTM\_Program"}$.
2. $Q_R = Q_U$ (state space preserved).
3. $\Sigma_R = \Gamma_U \setminus \{B_U\}$ (input symbols).
4. $\Gamma_R = \Gamma_U$ (tape alphabet preserved).
5. $B_R = B_U$ (blank symbol preserved).
6. $q_{\text{start},R} = q_{\text{start},U}$.
7. $q_{\text{halt},R} = q_{\text{halt},U}$.
8. $\delta_R(q, s) = \delta_U(q, s) = (q', s', d)$ (transition table preserved).
9. $\text{HistoryPolicy}_R = \text{RUTMHistoryPolicy}(\text{enabled}=\text{True}, \text{record\_schema}=(\text{"prev\_state"}, \text{"overwritten\_symbol"}, \text{"direction"}), \text{inverse\_policy}=\text{"LIFO\_stack"})$.
10. $\text{Provenance}_R = \text{RUTMProvenance}(\text{source\_model}=\text{"UTM-IR"}, \text{source\_stage}=\text{"Stage 6"}, \text{proof\_reference}=\text{"docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md"})$.

---

## 4. Configuration Mapping Function $E_{UR}$

The configuration mapping function $E_{UR} : \mathcal{C}_{\text{UTM}} \to \mathcal{C}_R$ maps source configurations to target configurations:

$$E_{UR}(q, T, h, k, \text{halted}, \text{error}) = (q, T, h, (), k, \text{halted}, \text{error})$$

For the initial configuration $C_{U,0} = (q_{\text{start}}, T_0, 0, 0, \text{False}, \text{None})$:
$$E_{UR}(C_{U,0}) = (q_{\text{start}}, T_0, 0, (), 0, \text{False}, \text{None})$$
which satisfies representation invariant $k = |()| = 0$.

---

## 5. Single-Step and Finite-Trace Semantic Preservation

By Stage 4 Theorem 3 (Commuting Diagram Theorem), the canonical projection $\pi_{\text{UTM}}(q, T, h, H, k, \text{halted}, \text{error}) = (q, T, h, k, \text{halted}, \text{error})$ satisfies:

$$\forall i \in \{0, \dots, n\}, \quad \pi_{\text{UTM}}(C_{R,i}) = C_{U,i}$$

where $C_{R,0} = E_{UR}(C_{U,0})$, $C_{R,i+1} = R(C_{R,i}, T_{UR}(U))$, and $C_{U,i+1} = \text{step\_utm}(C_{U,i}, U)$.

---

## 6. Halting & Error Boundaries

- **Halt Correspondence:** If $C_{U,n}$ reaches $q_{\text{halt}}$, $C_{R,n}$ has $q = q_{\text{halt}}$ and $\text{halted} = \text{True}$.
- **Error Boundaries:** Invalid source UTM-IR objects return `TranslationResult(success=False, errors=(...))`. Undefined runtime transitions produce atomic error strings in target execution matching source UTM behavior.

---

## 7. Reversibility & Conceptual Boundary

> [!IMPORTANT]
> **REVERSIBILITY BOUNDARY:**  
> The translator $T_{UR}$ maps classical UTM descriptions to reversible RUTM descriptions.  
> Source UTM programs remain classical. Reversibility is an operational property of the target RUTM execution environment ($R_P^{-1} \circ R_P = \text{id}$) established in Stage 4.

---

## 8. Proof Obligations Formulated for Stage 6

1. **Obligation A (Validity Preservation):** $\forall U \in \text{UTM-IR}_{\text{valid}}, T_{UR}(U) \in \text{RUTM-IR}_{\text{valid}}$.
2. **Obligation B (Initial Configuration Projection):** $\pi_{\text{UTM}}(E_{UR}(C_{U,0})) = C_{U,0}$.
3. **Obligation C (Single-Step Commutativity):** $\pi_{\text{UTM}}(R(E_{UR}(C_U), T_{UR}(U))) = \text{step\_utm}(C_U, U)$.
4. **Obligation D (Finite-Trace Preservation):** $\forall i \in \{0..n\}, \pi_{\text{UTM}}(C_{R,i}) = C_{U,i}$.
5. **Obligation E (Halt State Agreement):** $C_{R,n}.\text{halted} \iff C_{U,n}.\text{halted}$.

---

## 9. Stage 7 Prerequisites

Before proceeding to **Stage 7 (RUTM Execution Engine & Multi-Step Simulator)**:
1. Verify `src/module2/translation/` package passes all 20 unit tests in `tests/module2/test_stage6_utm_to_rutm.py`.
2. Verify Golden PoC pipeline passes differential execution check against source UTM program.
3. Verify frozen Module 1 regression suite (79/79 PASS) and Module 2 regression suite (78/78 PASS).
4. Obtain explicit user authorization to advance to Stage 7.
