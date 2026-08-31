# MODULE 7 STAGE 1 — TERMINOLOGY & LEXICON

- **Backend ID (`backend_id`)**: Unique string identifier of a backend instance (e.g., `LOCAL_REF_SIM_01`, `IBM_TORONTO`).
- **Provider ID (`provider_id`)**: Unique string identifier of the infrastructure provider (e.g., `LOCAL_REFERENCE`, `IBM`, `AWS_BRAKET`).
- **Backend Type (`backend_type`)**: Explicit classification enum/string (`VIRTUAL_SIMULATOR` vs `PHYSICAL_HARDWARE`).
- **Capability Model ($C_{\text{backend}}$)**: Immutable description of target device qubit count, native gate set, coupling map, max shots, and capability version.
- **Topology Coupling Map (`topology_coupling_map`)**: Directed/undirected physical qubit coupling edges `((q_i, q_j), ...)`.
- **Capability Hash (`capability_hash`)**: 64-character SHA-256 hex digest computed over canonical capability JSON payload.
