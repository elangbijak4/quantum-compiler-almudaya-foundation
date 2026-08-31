# Module 5 Scope Specification

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Status:** FORMALLY CLOSED / FROZEN (Scope & Constitutional Review)  

---

## 1. Frozen Scope Classification Table (20 Items)

Every candidate responsibility for Module 5 is formally classified into one of:
`CONFIRMED`, `PROVISIONAL`, `DEFERRED`, `FORBIDDEN`.

| # | Candidate Responsibility | Classification | Rationale & Semantic Boundary |
| :--- | :--- | :--- | :--- |
| **1** | `QuantumCircuitIR` Ingestion | `CONFIRMED` | Frozen entry point contract from Module 4 |
| **2** | Circuit Validation | `CONFIRMED` | AST & semantic validation of ingested `QuantumCircuitIR` prior to execution |
| **3** | Logical Execution | `CONFIRMED` | Execution of backend-independent logical circuit on reference simulator |
| **4** | State-Vector Simulation | `CONFIRMED` | Reference exact $\mathbb{C}^{2^N}$ state-vector evolution engine |
| **5** | Measurement | `CONFIRMED` | Computational-basis readout, sampling, and counts aggregation |
| **6** | Backend Abstraction | `CONFIRMED` | Pluggable interface contract (`CircuitExecutionBackend`) for simulation & hardware |
| **7** | Backend Capability Model | `CONFIRMED` | Protocol describing target engine constraints, topology, and native gate sets |
| **8** | Logical-to-Physical Mapping | `CONFIRMED` | Abstract-to-physical qubit allocation layer producing `PhysicalCircuitIR` |
| **9** | Physical Qubit Allocation | `CONFIRMED` | Mapping logical data & ancilla qubits to physical device node IDs |
| **10** | SWAP Routing | `CONFIRMED` | Insertion of SWAP gates for physical coupling graph connectivity constraints |
| **11** | Native Gate Translation | `CONFIRMED` | Decomposing primitive gates ($X, \text{CNOT}, \text{TOFFOLI}$) into target hardware native gates |
| **12** | Hardware Topology | `CONFIRMED` | Graph representation of physical qubit coupling and device connectivity |
| **13** | Noise Simulation | `DEFERRED` | Post-baseline enhancement; MUST NOT pollute ideal unitary baseline contract |
| **14** | External Simulator | `PROVISIONAL` | Supported via pluggable backend adapter interface |
| **15** | Real Hardware Execution | `DEFERRED` | Live remote physical device API execution deferred to post-baseline |
| **16** | Remote Job Submission | `DEFERRED` | Remote API orchestration, credential management, and polling deferred |
| **17** | Result Retrieval | `CONFIRMED` | Uniform structured `ExecutionResult` extraction from any backend |
| **18** | Pulse Control | `FORBIDDEN` | Out of scope; violates circuit-level compiler abstraction boundary |
| **19** | Calibration | `FORBIDDEN` | Low-level device control out of scope for quantum compiler |
| **20** | Readout Mitigation | `DEFERRED` | Advanced post-processing error mitigation deferred to post-baseline |

---

## 2. Decision Summary on Primary Initialization Questions

1. **Physicalization Boundary (`CONFIRMED`):**
   - Logical-to-physical mapping, SWAP routing, hardware topology representation, and native gate translation are **CONFIRMED** for Module 5.
   - **Mandatory Isolation Rule:** Physicalization operates strictly downstream of logical synthesis and produces a separate `PhysicalCircuitIR`. `QuantumCircuitIR` remains 100% frozen.
2. **Hardware Submission Boundary (`DEFERRED`):**
   - Live external physical device submission, remote API credential management, and job polling are **DEFERRED** to post-baseline.
   - Module 5 focuses on local reference state-vector simulation, shot-based sampling, and pluggable backend abstractions.
3. **Noise Simulation Boundary (`DEFERRED`):**
   - Noisy simulation channels (depolarizing, amplitude damping) are **DEFERRED** to post-baseline.
   - Module 5 enforces exact ideal unitary simulation ($U_C^\dagger U_C = I$) as its primary execution baseline.
