# Module 4 Completion Criteria (Constitutional Baseline)

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN CRITERIA  

---

## 1. Module 4 Completion Categories

For Module 4 to be certified `COMPLETE / FROZEN` in the future, the following 14 completion criteria must be satisfied:

1. **QTM-IR Consumption:** Successful ingestion of validated `QTMIRModel` instances.
2. **Finite-Domain Contract:** Validation of finite configuration domain $D_\text{fin}$ closure under $R_P$ ($R_P(D_\text{fin}) \subseteq D_\text{fin}$) and $R_P^{-1}$ ($R_P^{-1}(D_\text{fin}) \subseteq D_\text{fin}$).
3. **Injective Register Encoding:** Proof and verification of injective encoding $E : D_\text{fin} \to \{0,1\}^n$ ($C_1 \neq C_2 \implies E(C_1) \neq E(C_2)$).
4. **Logical History Preservation:** Encoding of classical history $H$ into registers when non-empty.
5. **Canonical Gate Realization:** Realization of transitions using canonical reversible gates ($\text{Toffoli}+\text{CNOT}+\text{X}$).
6. **Circuit IR Generation:** Generation of valid, structured `QuantumCircuitIR` models.
7. **Restricted-Domain Semantic Preservation:** Verification of $U_C |E(C)\rangle = |E(R_P(C))\rangle$ for all $C \in D_\text{fin}$.
8. **Gate Decomposition & Uncomputation:** Correct gate decomposition and verified clean Bennett uncomputation of all physical ancillas back to $|0\rangle$.
9. **Circuit Validation:** Structural and semantic validation via `validate_quantum_circuit_ir()`.
10. **3-Level Equivalence Verification Gate:** Automated equivalence check between QTM execution and circuit simulation (Symbolic, State Vector Norm $\epsilon < 10^{-12}$, Operator Norm $\epsilon < 10^{-12}$).
11. **Deterministic Synthesis:** 100% reproducible circuit generation from identical inputs.
12. **Complete Provenance Chain:** Preserving $\text{RUTM} \to \text{RUTM-IR} \to \text{QTM-IR} \to \text{Circuit-IR}$.
13. **Negative-Path Testing:** Robust rejection of non-finite domains, non-injective encodings, dirty ancillas, or corrupted gates.
14. **Cross-Module Regression:** 100% PASS on Module 1 (79/79), Module 2 (155/155), and Module 3 (131/131) test baselines.
