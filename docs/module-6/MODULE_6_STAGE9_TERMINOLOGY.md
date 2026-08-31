# MODULE 6 STAGE 9 — GLOSSARY & TERMINOLOGY

## Terminology Definitions

- **Resource Profile**: Immutable vector of exact logical resource metrics (qubits, data qubits, ancillas, gate counts, depth, T-depth, CNOT-depth, distribution) derived without physical hardware execution.
- **Quality Profile**: Multi-objective analytical object combining semantic validity, feasibility, resource profile, vocabulary compatibility, and optimization reduction.
- **Pareto Trade-off Analysis**: Evaluation of candidate compilation results to identify non-dominated peers across conflicting dimensions (e.g. gate count vs depth).
- **Result Classification**: Governed classification tag (`SEMANTICALLY_VALID`, `FEASIBLE`, `OPTIMIZED`, `NON_DOMINATED`, `DOMINATED`, `RESOURCE_CONSTRAINT_VIOLATION`, `INVALID`).
- **Non-Implication Rule**: Constitutional rule forbidding automatic inference between distinct properties (e.g., lower gate count does not imply universal superiority).
