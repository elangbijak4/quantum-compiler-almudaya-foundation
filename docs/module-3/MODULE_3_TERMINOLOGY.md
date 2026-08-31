# Module 3 Terminology & Glossary Specification

**Module:** Module 3 (Reversible UTM $\to$ Quantum Turing Machine / Quantum Abstraction Layer)  
**Status:** PRE-STAGE-1 MICRO CLOSURE PATCH COMPLETE / READY FOR STAGE 1  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`MODULE_3_CONSTITUTION.md`](MODULE_3_CONSTITUTION.md), [`MODULE_3_SCOPE.md`](MODULE_3_SCOPE.md)  

---

## 1. Frozen Terminology (Preserved from Modules 1 & 2)

- **UTM / UTMProgram:** Classical Universal Turing Machine 7-tuple $(\mathcal{Q}, \Sigma, \Gamma, B, q_0, q_{\text{halt}}, \delta_U)$ (Module 1).
- **UTMConfiguration:** Classical state $C_U = (q, T, h, k, \text{halted}, \text{error})$ (Module 1).
- **RUTM:** Reversible Universal Turing Machine 10-tuple (Module 2 Stage 1).
- **RUTMConfiguration:** Reversible state $C_R = (q, T, h, H, k, \text{halted}, \text{error})$ with history stack $H$ (Module 2 Stage 2).
- **RUTM-IR:** Intermediate Representation for reversible Turing machines (Module 2 Stage 5).
- **$\pi_{\text{UTM}}$ Projection:** Projection operator mapping reversible state $C_R$ to classical state $C_U$ by dropping $H$ (Module 2 Stage 4).

---

## 2. Module 3 Quantum Abstraction Terminology

- **QTM (Quantum Turing Machine):** Quantum computational abstraction defined by Hilbert space $\mathcal{H}_Q$, basis states $|C_R\rangle$, and unitary state transition matrix $U_P$.
- **`QTM-IR`:** Intermediate Representation for Quantum Turing Machines / Unitary Machine Abstractions (Module 3 Target).
- **Computational Basis State ($|C_R\rangle$):** Quantum state vector in Hilbert space $\mathcal{H}_Q$ corresponding to discrete classical reversible configuration $C_R$.
- **Unitary Transition Operator ($U_P$):** Linear operator $U_P = \sum |R_P(C)\rangle \langle C|$ satisfying $U_P^\dagger U_P = I$ representing single-step quantum state evolution.
- **State Vector ($|\psi_t\rangle$):** Normalized vector in Hilbert space $\mathcal{H}_Q$ representing quantum state at step $t$.
- **Adjoint Evolution / Inverse Computational Evolution ($U_P^\dagger$):** Hermitian conjugate operator satisfying $U_P^\dagger |R_P(C)\rangle = |C\rangle$. Represents mathematical inverse computational evolution (*must not be described as physical hardware or thermodynamic time reversal*).
- **Transition-Closed Finite Domain ($\mathcal{C}_{R,\text{fin}}$):** Finite configuration subspace satisfying $R_P(\mathcal{C}_{R,\text{fin}}) \subseteq \mathcal{C}_{R,\text{fin}}$ and bijectivity under $R_P$, necessary for a valid finite matrix representation $[U_P]$.
- **Global Bijectivity:** Requirement that $R_P$ is total, injective, and surjective over $\mathcal{C}_R$, ensuring $U_P$ is unitary over $\mathcal{H}_Q$.
- **Quantum Basis Fidelity ($\mathcal{F}$):** Measure of overlap between target quantum state $|\psi\rangle$ and reference basis state $|C_R\rangle$, defined as $\mathcal{F} = |\langle C_R | \psi \rangle|^2$.
- **Logical History Stack ($H$):** Logical reversible machine variable in Module 3 (distinct from quantum ancilla qubits in Module 4).
- **Quantum Ancilla Qubits:** Auxiliary qubits allocated during physical circuit realization (Module 4 concept).
- **Uncomputation Obligation:** Mathematical protocol for resetting history registers ($U_P^\dagger |C_{\text{final}}\rangle = |C_0\rangle$) to prevent garbage entanglement.
