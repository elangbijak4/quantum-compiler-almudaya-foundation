# 01. CLI Command Reference Manual

Comprehensive technical reference for all 13 production CLI commands.

---

## Command Summary Matrix

| Category | Command | Target Core Authority | Required Arguments | Optional Flags | Exit Codes |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Pipeline** | `compile` | Modules 1–7 Pipeline | `input` | `--backend`, `--shots`, `--seed` | 0, 1, 2, 99 |
| **Transformation** | `aml` | Module 1 (AML Parser) | `input` | — | 0, 1, 2, 99 |
| **Transformation** | `utm` | Module 2 (UTM IR) | `artifact` | — | 0, 1, 2, 99 |
| **Transformation** | `rutm` | Module 3 (Reversible UTM) | `artifact` | — | 0, 1, 2, 99 |
| **Transformation** | `semantic` | Module 4 (Semantic Cert) | `artifact` | — | 0, 1, 2, 99 |
| **Transformation** | `map` | Module 5 (Quantum Mapping) | `artifact` | — | 0, 1, 2, 99 |
| **Transformation** | `optimize` | Module 6 (Pareto Optimizer) | `artifact` | — | 0, 1, 2, 99 |
| **Transformation** | `lower` | Module 7 Stage 2 (Lowering) | `artifact` | `--backend` | 0, 1, 2, 99 |
| **Execution** | `simulate` | Module 7 Stage 3 (Simulator) | `artifact` | `--shots`, `--seed` | 0, 1, 3, 99 |
| **Execution** | `execute` | Module 7 Stage 4 (Provider) | `artifact` | `--backend`, `--provider`, `--shots`, `--credential-ref` | 0, 1, 3, 99 |
| **Validation** | `verify` | Module 7 Stage 5 (Verification) | `artifact` | `--policy` | 0, 1, 4, 5, 99 |
| **Inspection** | `inspect` | Core Read-Only API | `artifact` | `--backend` | 0, 1, 99 |
| **Inspection** | `lineage` | Module 6 Stage 11 (Lineage) | `artifact` | — | 0, 1, 99 |

---

## Exit Code Taxonomy
- `0 (SUCCESS)`: Command executed successfully.
- `1 (INVALID_USER_INPUT)`: Syntax error, missing argument, or invalid options.
- `2 (COMPUTATIONAL_FAILURE)`: Core compilation, lowering, or mapping failure.
- `3 (EXECUTION_FAILURE)`: Simulator or backend submission failure.
- `4 (VERIFICATION_REJECTED)`: Statistical verification decision `REJECTED`.
- `5 (VERIFICATION_INCONCLUSIVE)`: Statistical verification decision `INCONCLUSIVE`.
- `99 (INTERNAL_ERROR)`: Unexpected internal application error.
