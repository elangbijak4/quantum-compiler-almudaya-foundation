# Module 4 Terminology & Glossary

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN TERMINOLOGY  

---

## 1. Core Terminology Definitions

- **QTM-IR:** Quantum Turing Machine Intermediate Representation (Module 3 output).
- **Quantum Circuit IR:** Backend-independent quantum circuit representation (Module 4 output).
- **Finite Domain ($D_\text{fin}$):** A declared finite set of classical configurations $D_\text{fin} \subset \mathcal{C}_R$ closed under $R_P$ and $R_P^{-1}$.
- **Register Encoding ($E$):** An injective mapping $E : D_\text{fin} \to \{0,1\}^n$ mapping classical configurations into $n$-qubit bitstrings.
- **Canonical Reversible Gate Set:** The primary logical gate set ($\text{Toffoli} + \text{CNOT} + \text{X}$) used to synthesize QTM transition operators.
- **Qubit Register:** Named group of logical qubits (State, Tape, Head, History, Ancilla).
- **Logical History ($H$):** Step history sequence in classical configuration $C$ preserving reversibility.
- **Physical Ancilla:** Temporary workspace qubits allocated for gate synthesis and uncomputed back to $|0\rangle$.
- **Physical Garbage:** Transient intermediate states on physical ancillas prior to uncomputation.
- **Bennett Uncomputation:** The reversible procedure $f(x, 0) \to (x, g(x)) \to (x, 0)$ clearing workspace ancillas.
- **Restricted-Domain Operator Equivalence:** Equivalence condition $U_C |E(C)\rangle = |E(R_P(C))\rangle$ for all $C \in D_\text{fin}$.
- **3-Level Verification Policy:** Symbolic basis matching, state vector norm comparison ($\epsilon < 10^{-12}$), and matrix operator norm comparison ($\epsilon < 10^{-12}$).
- **Transpilation Firewall:** The strict architectural boundary separating Module 4 logical synthesis from Module 5 physical hardware transpilation.

---

## 2. Inviolable Terminology Distinctions

> [!IMPORTANT]
> - **Logical History ($H$):** Part of classical state tuple $C$; MUST be encoded in configuration register if non-empty.
> - **Physical Ancilla:** Scratchpad workspace qubit in Module 4; MUST return to $|0\rangle$ at circuit termination.
> - **Logical Qubit Synthesis (Module 4):** Abstract circuit construction without physical topology constraints.
> - **Physical Qubit Transpilation (Module 5):** Hardware routing, swap insertion, and pulse control.
