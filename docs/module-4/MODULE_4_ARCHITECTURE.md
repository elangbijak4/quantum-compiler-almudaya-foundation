# Module 4 Architecture — Layered Synthesis & Realization Model

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN ARCHITECTURE  

---

## 1. Architectural Layers & Boundaries

Module 4 is structured into six strictly decoupled layers:

```
+-------------------------------------------------------------+
| 1. QTM-IR Input Boundary Layer (Module 3 Contract)         |
+-------------------------------------------------------------+
                              ↓
+-------------------------------------------------------------+
| 2. Finite Domain & Injective Encoding Layer                 |
+-------------------------------------------------------------+
                              ↓
+-------------------------------------------------------------+
| 3. Quantum Circuit Intermediate Representation (Circuit-IR) |
+-------------------------------------------------------------+
                              ↓
+-------------------------------------------------------------+
| 4. Reversible Gate Realization Layer (Toffoli + CNOT + X)   |
+-------------------------------------------------------------+
                              ↓
+-------------------------------------------------------------+
| 5. Gate Decomposition & Bennett Uncomputation Layer         |
+-------------------------------------------------------------+
                              ↓
+-------------------------------------------------------------+
| 6. Circuit Equivalence & Verification Gate Layer (3-Level)  |
+-------------------------------------------------------------+
```

---

## 2. Gate Architecture & Numerical Equivalence Policy

### 2.1 Two-Stage Gate Architecture
1. **Primary Logical Reversible Gate Set (`CONFIRMED`):** $\text{Toffoli} + \text{CNOT} + \text{X}$ serves as the canonical logical gate representation for realizing classical reversible transitions $R_P$ unitarily.
2. **Decomposition Target Layer (`PROVISIONAL`):** Multi-controlled Toffoli gates decompose into primitive 1-qubit/2-qubit gates during Stage 4.

### 2.2 3-Level Equivalence Verification Policy
- **Level 1 (Exact Symbolic Basis Correspondence):** $E(R_P(C)) = \text{Permutation}(E(C))$. Exact bitstring identity.
- **Level 2 (Numerical State Vector Comparison):** $\|\psi_\text{circuit} - \psi_\text{QTM}\|_2 < \epsilon$ with $\epsilon = 10^{-12}$.
- **Level 3 (Matrix Operator Comparison):** $\|U_C - U_P|_{D_\text{fin}}\|_\infty < \epsilon$ with $\epsilon = 10^{-12}$.
