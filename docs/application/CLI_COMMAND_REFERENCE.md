# APPLICATION / PRODUCT LAYER — CLI COMMAND REFERENCE

## Command Reference Matrix

| Category | Command | Target Core Module / Stage | Required Arguments | Optional Flags |
| :--- | :--- | :--- | :--- | :--- |
| **Pipeline** | `compile` | Modules 1–7 Pipeline | `input` | `--backend`, `--shots`, `--seed` |
| **Stepwise** | `aml` | Module 1 | `input` | — |
| **Stepwise** | `utm` | Module 2 | `artifact` | — |
| **Stepwise** | `rutm` | Module 3 | `artifact` | — |
| **Stepwise** | `semantic` | Module 4 | `artifact` | — |
| **Stepwise** | `map` | Module 5 | `artifact` | — |
| **Stepwise** | `optimize` | Module 6 | `artifact` | — |
| **Stepwise** | `lower` | Module 7 Stage 2 | `artifact` | `--backend` |
| **Execution** | `simulate` | Module 7 Stage 3 | `artifact` | `--shots`, `--seed` |
| **Execution** | `execute` | Module 7 Stage 4 | `artifact` | `--backend`, `--provider`, `--shots`, `--credential-ref` |
| **Validation** | `verify` | Module 7 Stage 5 | `artifact` | `--policy` |
| **Inspection** | `inspect` | Core Read-Only API | `artifact` | `--backend` |
| **Inspection** | `lineage` | Module 6 Stage 11 | `artifact` | — |
