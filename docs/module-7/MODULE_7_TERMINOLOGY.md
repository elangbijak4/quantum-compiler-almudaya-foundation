# MODULE 7 — TERMINOLOGY & LEXICON

- **Logical Circuit**: High-level, provider-neutral quantum circuit produced and certified by Module 6.
- **Native Circuit**: Backend-specific quantum circuit compiled into the native gate set and topology graph of target backend ($C_{\text{backend}}$).
- **Backend Capability Model ($C_{\text{backend}}$)**: Data contract specifying device native gates, qubit limits, topology coupling map, max shots, and execution constraints.
- **Logical-to-Native Lowering**: Transpilation pass that maps logical gates to native gates and logical qubits to physical device topology.
- **Reference Simulator**: Local virtual simulator executing native circuits deterministically without external network APIs.
- **Execution Job**: Computational unit representing circuit submission, status tracking, and shot measurement retrieval.
- **Statistical Result Verification**: Mathematical analysis comparing observed execution shot distributions against reference distributions (e.g. Hellinger distance).
- **Credential Reference**: Non-sensitive string referencing a credential stored in runtime environment or secret manager (`credential_ref: "env:..."`).
