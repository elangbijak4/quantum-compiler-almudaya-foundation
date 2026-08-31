# Module 5 Terminology & Definitions

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Status:** FORMALLY CLOSED / FROZEN (Constitutional Review)  

---

## 1. Domain Terminology Definitions

- **Logical Circuit (`QuantumCircuitIR`):** Backend-independent quantum circuit representation emitted by Module 4, operating on abstract data registers and clean workspace ancillas.
- **Physical Circuit (`PhysicalCircuitIR`):** Target-specific quantum circuit mapped to physical qubit node IDs, physical device coupling graphs, and hardware-native gates.
- **Physicalization:** The compilation transformation ($\text{Phy}: \text{QuantumCircuitIR} \to \text{PhysicalCircuitIR}$) performing logical-to-physical qubit mapping, physical SWAP routing, and native gate translation while preserving logical semantics ($\text{Sem}(C_P) \equiv \text{Sem}(C_L)$).
- **Backend (`CircuitExecutionBackend`):** Execution target engine (e.g., state-vector simulator or hardware adapter).
- **State-Vector Simulator:** Reference exact numerical backend computing state-vector linear transformations $\psi \mapsto U \psi$ in $\mathbb{C}^{2^N}$.
- **Shot:** A single computational-basis measurement sample executed on a quantum circuit.
- **Measurement Outcome:** Sampled bitstring or probability distribution over computational basis states $|k\rangle$.
- **Backend Capability:** Declaration of constraints and features supported by a backend (e.g., maximum width, coupling graph, native gate set).
- **Execution Provenance:** Cryptographic or structured log linking execution results back to source RUTM hash, QTM machine ID, and stage synthesis metadata.
- **SWAP Routing:** Insertion of SWAP gates to satisfy physical device coupling graph connectivity constraints.
