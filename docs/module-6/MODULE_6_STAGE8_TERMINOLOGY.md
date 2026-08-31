# MODULE 6 STAGE 8 — GLOSSARY & TERMINOLOGY

## Terminology Definitions

- **Synthesis Cost Metrics**: Quantitative resource bounds of a quantum circuit IR (gate count, T-depth, CNOT-depth, total depth, qubit width).
- **Canonical Algebraic Rewriting**: Semantics-preserving transformations (e.g. self-inverse gate cancellation, identity elimination) operating within $G_{\text{effective}}$.
- **Gate Count Reduction**: Non-negative integer difference $\text{GateCount}(Q_{\text{orig}}) - \text{GateCount}(Q_{\text{opt}})$.
- **Vocabulary Containment**: Property that every gate in $Q_{\text{opt}}$ is a member of the resolved $G_{\text{effective}}$.
- **Optimization Cost Report**: Immutable data structure documenting optimization metrics, status, semantic equivalence verification, and provenance.
