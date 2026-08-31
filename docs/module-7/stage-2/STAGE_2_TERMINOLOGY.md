# MODULE 7 STAGE 2 — TERMINOLOGY & LEXICON

- **Logical Circuit**: High-level quantum circuit output from Module 6 Stage 10 carrying semantic verification evidence.
- **Native Circuit**: Backend-compatible quantum circuit derived by lowering logical gates to `backend.native_gate_set` and mapping to physical topology.
- **Lowering**: The process of decomposing logical operations and mapping registers to backend constraints.
- **Decomposition**: Algorithmic transformation of a logical gate into an equivalent sequence of backend native gates.
- **Logical Qubit ($q_{\text{logical}}$)**: Virtual quantum register index referenced in high-level logical circuit.
- **Physical Qubit ($q_{\text{physical}}$)**: Physical quantum hardware qubit index on target backend device ($C_{\text{backend}}$).
- **Qubit Mapping (`qubit_mapping`)**: Explicit dictionary mapping logical qubit indices to physical device indices.
- **Routing**: Insertion of SWAP gates or remapping passes to satisfy target backend coupling map constraints.
- **Lowering Policy (`LoweringPolicy`)**: Explicit configuration object governing decomposition, mapping, and routing rules.
- **Candidate Circuit**: A lowered native circuit prior to semantic verification confirmation.
- **Verified Circuit**: A candidate native circuit whose semantic equivalence to original logical circuit is confirmed by Module 4 Stage 4 authority.
