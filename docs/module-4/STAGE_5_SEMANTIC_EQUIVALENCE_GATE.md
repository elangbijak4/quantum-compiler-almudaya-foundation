# Stage 5 Specification — Circuit Semantic Equivalence & End-to-End Synthesis Gate

**Module:** Module 4 — Quantum Circuit Synthesis  
**Stage:** Stage 5 — Circuit Semantic Equivalence & End-to-End Synthesis Gate  
**Status:** FORMALLY CLOSED / FROZEN  

---

## 1. Primary Objective & Central Semantic Invariant

Stage 5 establishes the executable end-to-end semantic equivalence gate for the complete compilation chain:

$$\text{RUTM} \longrightarrow \text{RUTM-IR} \longrightarrow \text{QTM-IR} \longrightarrow \text{Stage 3 Circuit-IR} \longrightarrow \text{Stage 4 Decomposed Circuit-IR}$$

### Central Semantic Invariant
For every $C \in D_\text{fin}$:
$$U_4 |E(C)\rangle = U_3 |E(C)\rangle = |E(R_P(C))\rangle$$

Equivalently:
$$U_4 \circ \iota_\text{fin} = U_3 \circ \iota_\text{fin} = \iota_\text{fin} \circ R_P \quad \text{over } D_\text{fin}$$

---

## 2. End-to-End Verification Gate Architecture (`EquivalenceGate`)

The `EquivalenceGate` class (`src/module4/equivalence/gate.py`) verifies the compilation pipeline across multi-step execution horizons ($t = 0 \dots T$):

1. **AST Validation:** Output circuit validated via `validate_circuit_ir()`.
2. **Domain & Encoding Invariants:** Verifies $R_P(D_\text{fin}) \subseteq D_\text{fin}$, $R_P^{-1}(D_\text{fin}) \subseteq D_\text{fin}$, and encoding injectivity $E(C_1) = E(C_2) \implies C_1 = C_2$.
3. **Multi-Step & Every-Step Equivalence:** Evaluates $U_3 |E(C_t)\rangle = |E(C_{t+1})\rangle$ and $U_4 |E(C_t)\rangle = |E(C_{t+1})\rangle$ at every step $t$.
4. **Direct Stage 3 / Stage 4 Equivalence:** Verifies $U_4 |E(C_t)\rangle = U_3 |E(C_t)\rangle$.
5. **Reverse Execution Equivalence:** Verifies $U_4^\dagger |E(C_{t+1})\rangle = |E(C_t)\rangle$ and $U_3^\dagger |E(C_{t+1})\rangle = |E(C_t)\rangle$.
6. **Ancilla Cleanliness:** Verifies output ancilla register is $|0 \dots 0\rangle$ (`CLEAN`).
7. **History Preservation:** Verifies $H_1 \neq H_2 \implies E(C_1) \neq E(C_2)$.
8. **Halting & Error Semantics:** Fixed-point states satisfy $U_4 |E(C_\text{halt})\rangle |0_A\rangle = |E(C_\text{halt})\rangle |0_A\rangle$ and $U_4 |E(C_\text{error})\rangle |0_A\rangle = |E(C_\text{error})\rangle |0_A\rangle$.
9. **Superposition & Complex Amplitudes:** Verifies $\|U_4 \psi - U_3 \psi\|_2 < 10^{-12}$ and $\|U_4 \psi\|_2 = \|\psi\|_2$.
10. **Operator Unitarity & Correspondence:** Verifies $\|U_4^\dagger U_4 - I\|_2 < 10^{-12}$, $\|U_4 U_4^\dagger - I\|_2 < 10^{-12}$, and matrix semantic correspondence.
11. **Global Phase Preservation:** Verifies zero phase drift ($e^{i\phi} \equiv 1$).
12. **Provenance Chain:** Validates full $\text{RUTM} \to \text{RUTM-IR} \to \text{QTM-IR} \to \text{Stage 3} \to \text{Stage 4}$ metadata chain.
13. **Determinism:** Verifies 100% deterministic JSON output and execution.

---

## 3. Failure Localization & Diagnostics

`Stage5EquivalenceResult` reports independent sub-category status booleans:
- `source_semantics_pass`
- `encoding_pass`
- `transition_pass`
- `stage3_equivalence_pass`
- `stage4_equivalence_pass`
- `reverse_equivalence_pass`
- `superposition_pass`
- `ancilla_pass`
- `history_pass`
- `halting_pass`
- `error_pass`
- `operator_unitarity_pass`
- `provenance_pass`
- `determinism_pass`
- `failure_localization_pass`
- `negative_tests_pass`
