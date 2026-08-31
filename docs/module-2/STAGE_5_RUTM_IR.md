# Stage 5 Specification — RUTM-IR Model

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 5 — RUTM-IR Model  
**Status:** COMPLETE (FROZEN)  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`STAGE_1_RUTM_SPECIFICATION.md`](STAGE_1_RUTM_SPECIFICATION.md), [`STAGE_2_RUTM_CONFIGURATION.md`](STAGE_2_RUTM_CONFIGURATION.md), [`STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md`](STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md), [`STAGE_4_RUTM_REVERSIBILITY_PROOF.md`](STAGE_4_RUTM_REVERSIBILITY_PROOF.md)  
**Implementation Package:** [`src/module2/rutm_ir/`](../../src/module2/rutm_ir)  

---

## 1. Purpose

The purpose of Stage 5 is to establish the formal Intermediate Representation (IR) model for the Reversible Universal Turing Machine (`RUTM-IR`). 

RUTM-IR acts as the compiler-level data model representing static reversible machine descriptions, enabling serialization, verification, program transformations, and downstream compilation passes while remaining strictly faithful to the proven mathematical operational semantics of Stages 1–4.

$$\text{Mathematical RUTM (Stages 1--4)} \xrightarrow{\quad\text{representation}\quad} \text{RUTM-IR (Stage 5)} \xrightarrow{\quad\text{translation}\quad} \text{Future Stages}$$

---

## 2. Relationship to Stages 1–4

- **Stage 1 (RUTM Specification):** Defined the mathematical 8-tuple model $(Q, \Sigma, \Gamma, \delta_R, q_{\text{start}}, B, q_{\text{halt}}, H)$.
- **Stage 2 (RUTM Configuration Model):** Formalized extended runtime configuration $C_R = (q, T, h, H, k, \text{halted}, \text{error})$ and representation invariants ($k = |H|$).
- **Stage 3 (Operational Semantics):** Defined single-step forward transition $R(C_R, P)$ and reverse transition $R^{-1}(C'_R, P)$.
- **Stage 4 (Formal Proof):** Formally proved single-step reversibility ($R^{-1} \circ R = \text{id}$), finite-trace reversibility, and commuting projection diagram ($\pi_{\text{UTM}} \circ R = \delta \circ \pi_{\text{UTM}}$).
- **Stage 5 (RUTM-IR Model):** Provides the compiler data structures (`RUTM_IR`) and serialization routines to manipulate static machine descriptions without altering frozen semantics.

---

## 3. Formal Definition of RUTM-IR

Static machine descriptions in RUTM-IR are defined as the formal 10-tuple:

$$\text{RUTM\_IR} = (\text{name}, Q, \Sigma, \Gamma, B, q_{\text{start}}, q_{\text{halt}}, \delta_R, \text{HistoryPolicy}, \text{Provenance})$$

### Components:
1. `name` $\in \text{String}$: Machine or program identifier.
2. $Q \subset \text{String}$: Finite non-empty set of control states.
3. $\Sigma \subseteq \Gamma$: Finite non-empty input alphabet.
4. $\Gamma$: Finite non-empty tape alphabet (satisfying $\Sigma \subseteq \Gamma$).
5. $B \in \Gamma$: Blank symbol (default `"\_"`).
6. $q_{\text{start}} \in Q$: Initial control state.
7. $q_{\text{halt}} \in Q$: Terminal halting state.
8. $\delta_R : (Q \setminus \{q_{\text{halt}}\}) \times \Gamma \to Q \times \Gamma \times \{L, R, S\}$: Static transition table component.
9. $\text{HistoryPolicy}$: Specification of auxiliary history record schema (`enabled=True`, `record_schema=("prev_state", "overwritten_symbol", "direction")`, `inverse_policy="LIFO_stack"`).
10. $\text{Provenance}$: Metadata identifying proof grounding (`source_model="RUTM"`, `proof_reference="docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md"`).

> [!IMPORTANT]
> **$\delta_R$ TERMINOLOGY PRECISION:**  
> $\delta_R$ denotes the static transition table component of the RUTM representation, mapping $(q, s) \mapsto (q', s', d)$.  
> Reversibility is **NOT** an intrinsic property of $\delta_R$ in isolation, but of the complete RUTM operational construction ($\text{static transition action} + \text{runtime auxiliary history} + \text{reverse semantics}$) established and proven in Stage 4.

---

## 4. Program vs Configuration Separation & Immutability

RUTM-IR maintains a strict architectural boundary between static machine descriptions and dynamic execution state:

| Feature | `RUTM_IR` (Program IR) | `RUTMConfiguration` (Runtime State) |
| :--- | :--- | :--- |
| **Nature** | Static machine specification | Dynamic computational configuration |
| **Mutability** | Shallow Immutable (`@dataclass(frozen=True)`) | Mutable execution state |
| **Contents** | $Q, \Sigma, \Gamma, B, q_{\text{start}}, q_{\text{halt}}, \delta_R$, policies | $q, T, h, H, k, \text{halted}, \text{error}$ |
| **Lifecycle** | Created at compile time / load time | Evolves step-by-step during simulation |

> [!NOTE]
> **IMMUTABILITY PRECISION:**  
> `RUTM_IR` is implemented using `@dataclass(frozen=True)`, providing shallow structural immutability (preventing top-level attribute reassignment). Nested mutable containers such as the `transitions` dictionary are not deeply immutable at the Python runtime level, which is standard for Python dictionary-based IR models.

---

## 5. Transition Representation & History Policy

Static transition rules in `RUTM_IR` map exact state-symbol pairs to transition actions:
$$(q, s) \longmapsto (q', s', d)$$

The runtime history record $r = (q, s, d)$ captured during forward execution is NOT stored inside static `RUTM_IR`. Instead, `RUTM_IR` specifies `history_policy`, declaring the schema (`("prev_state", "overwritten_symbol", "direction")`) and LIFO stack policy (`"LIFO_stack"`) required by the proven Stage 3/4 RUTM semantics.

---

## 6. Validation Rules & Executable Validator

The validator `validate_rutm_ir(ir)` enforces strict representation integrity:
1. **Name Non-Emptiness:** `name` must be a valid non-empty string.
2. **State Set Integrity:** $Q$ is non-empty, contains valid strings, $q_{\text{start}} \in Q$, and $q_{\text{halt}} \in Q$.
3. **Alphabet Inclusion:** $\Sigma \subseteq \Gamma$, $B \in \Gamma$.
4. **Transition Determinism:** For each key $(q, s)$, at most one action exists.
5. **Boundary Restrictions:** No transitions originate from $q_{\text{halt}}$.
6. **Action Target Validity:** Transition targets $q' \in Q$, write symbols $s' \in \Gamma$, directions $d \in \{L, R, S\}$.
7. **History Policy Integrity:** `enabled=True` requires exact `record_schema=("prev_state", "overwritten_symbol", "direction")` and `inverse_policy="LIFO_stack"`.
8. **Provenance Metadata Integrity:** Source model, stage, and proof reference must be present and valid.

---

## 7. Deterministic Serialization & Canonical Format

RUTM-IR provides canonical JSON serialization via `serialize_rutm_ir(ir)` and deserialization via `deserialize_rutm_ir(json_str)`:
- Sets $Q, \Sigma, \Gamma$ are sorted lexicographically during serialization.
- Transition rules are sorted deterministically by `(current_state, read_symbol)`.
- Reconstructed `RUTM_IR` objects satisfy exact round-trip equality:
$$\text{deserialize\_rutm\_ir}(\text{serialize\_rutm\_ir}(\text{ir})) == \text{ir}$$

---

## 8. Semantic Identity & IR $\to$ Configuration Relationship

- `ir.to_utm_program()` converts `RUTM_IR` to Module 1's frozen `UTMProgram`.
- `create_initial_configuration_from_ir(ir, tape=None)` instantiates Stage 2's frozen `RUTMConfiguration`. Initial head position (`head_pos = 0`) follows frozen Stage 2 initial configuration semantics.
- Execution of Stage 3 operational semantics (`forward_step_rutm`, `reverse_step_rutm`) using IR-derived models produces exact behavioral equivalence with Stage 1–4 specifications.

---

## 9. Non-Claims & Explicit Boundaries

1. **Representation $\neq$ Proof:** `validate_rutm_ir(ir)` verifies structural IR validity, not the mathematical proof of reversibility (proven in Stage 4).
2. **No Compiler/Translator Included:** Stage 5 defines the IR model; `UTM → RUTM` translation belongs to Stage 6.
3. **No Quantum Hardware Claims:** Quantum compilation belongs to Modules 3 & 4.

---

## 10. Stage 6 Prerequisites

Before advancing to **Stage 6 (UTM $\to$ RUTM Translation Specification)**:
1. Verify `src/module2/rutm_ir/` package passes all unit tests in `tests/module2/test_stage5_rutm_ir.py`.
2. Verify frozen Module 1 regression suite (79/79 PASS) and Module 2 regression suite (75/75 PASS).
3. Obtain explicit user authorization to advance to Stage 6.
