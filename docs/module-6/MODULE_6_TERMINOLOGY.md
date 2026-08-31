# Module 6 Terminology & Ontology Specification

**Module:** Module 6 — Classical-to-Quantum Expressibility & Equivalence Analysis  
**Status:** FORMALLY CLOSED / FROZEN (Micro-Closure)  

---

## 1. Precise Domain Definitions

To prevent ambiguous or conflated scientific claims, the following terms MUST be used strictly according to their formal definitions:

- **Classical Algorithm ($A_C$):** Defined at $A_\text{semantic}$ as the finite transition system $(D_\text{fin}, R_P)$ over $D_\text{fin} \subset C_R$ ($|D_\text{fin}| < \infty$).
- **AML:** Abstract Machine Language (Module 1 source representation).
- **RUTM:** Reversible Universal Turing Machine (Module 1 intermediate reversible representation).
- **QTM:** Quantum Turing Machine transition & tape execution model (Module 2 representation).
- **Quantum Circuit ($C_Q$):** Defined at $C_Q^\text{logical}$ as the logical `QuantumCircuitIR` AST space (Module 4 output contract).
- **Semantic Mapping ($F$):** The compiler-induced mapping $F: A_C \to C_Q^\text{logical}$.
- **Injective Mapping:** Syntactic injectivity ($F(a_1) = F(a_2) \implies a_1 = a_2$) versus semantic injectivity ($\bar{F}([a_1]) = \bar{F}([a_2]) \implies [a_1] = [a_2]$). Frozen as an **UNPROVEN RESEARCH PROPERTY**.
- **Surjective Mapping:** For every $c \in C_Q^\text{logical}$, there exists $a \in A_C$ such that $F(a) \equiv_Q c$. Frozen as an **UNPROVEN RESEARCH PROPERTY**.
- **Bijective Mapping:** $F$ is both injective and surjective.
- **Image ($\text{Img}(F)$):** The subset of quantum circuits $\{F(A) \mid A \in A_C\} \subset C_Q^\text{logical}$. Frozen as an **ANALYTICAL OBJECT**.
- **Expressibility:** The degree to which $\text{Img}(F)$ covers the full Hilbert space unitary group $U(2^N)$ or relevant circuit subspaces.
- **Embedding:** A structure-preserving injection of $A_C$ into $C_Q$.
- **Simulation Relation:** A behavioral relationship where $c \in C_Q$ step-by-step reproduces the execution trace of $a \in A_C$.
- **Counterexample:** A specific program or circuit instance demonstrating the invalidity of a hypothesis.
- **Hadamard Counterexample ($H \notin \text{Img}(F)$):** Frozen as an **OPEN HYPOTHESIS**.

---

## 2. Six Levels of Equivalence

1. **Level 1 — Algorithmic / Functional Equivalence:** Equality of input-output maps $f_A(x) = f_B(x)$ over classical data inputs.
2. **Level 2 — Configuration-Transition Equivalence:** 1-to-1 step-by-step mapping of classical computational configurations to quantum tape/register states.
3. **Level 3 — Computational-Basis Transformation Equivalence:** Exact equality of permutation matrices acting on computational basis vectors $|x\rangle \mapsto |f(x)\rangle$.
4. **Level 4 — Superposition / Linear Semantic Equivalence:** Preservation of linear state evolution over complex superposition vector spaces $(\mathbb{C}^2)^{\otimes N}$.
5. **Level 5 — Operator / Unitary Equivalence:** Matrix identity $U_A = U_B$ (or global phase equivalence $U_A = e^{i\phi} U_B$) up to workspace ancilla uncomputation.
6. **Level 6 — Measurement-Distribution Equivalence:** Identity of measurement probability distributions $P_A(x) = P_B(x)$ for all computational basis readouts.
