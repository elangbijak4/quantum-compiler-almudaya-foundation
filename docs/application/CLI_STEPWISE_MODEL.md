# APPLICATION / PRODUCT LAYER — CLI STEPWISE & COMPUTATIONAL INSPECTION MODEL

## 1. Executive Summary

The CLI Foundation supports two first-class operational modes:
1. **Pipeline Mode** (`compile <input>`): Convenience orchestration of the full compilation sequence.
2. **Stepwise / Computational Inspection Mode** (`aml`, `utm`, `rutm`, `semantic`, `map`, `optimize`, `lower`, `simulate`, `execute`, `verify`, `lineage`, `inspect`): Step-by-step transformation and inspection without executing the full pipeline.

## 2. Authorized Stepwise Command Set

| Category | Command | Target Core Module / Stage | Purpose |
| :--- | :--- | :--- | :--- |
| **Transformation** | `aml` | Module 1 | Classical Algorithm -> AML transformation |
| **Transformation** | `utm` | Module 2 | AML -> Universal Turing Machine IR |
| **Transformation** | `rutm` | Module 3 | UTM -> Reversible UTM IR |
| **Validation** | `semantic` | Module 4 | Reversible Gate Synthesis & Semantic Certification |
| **Transformation** | `map` | Module 5 | Quantum Qubit Mapping & Topology Physicalization |
| **Transformation** | `optimize` | Module 6 | Pareto Quality Optimization & Rule Rewrite |
| **Transformation** | `lower` | Module 7 Stage 2 | Deterministic Logical-to-Native Gate Lowering |
| **Execution** | `simulate` | Module 7 Stage 3 | Local Reference Quantum Simulator Execution |
| **Execution** | `execute` | Module 7 Stage 4 | Provider Adapter Hardware/Cloud Job Submission |
| **Validation** | `verify` | Module 7 Stage 5 | Statistical Verification (Hellinger & KS metrics) |
| **Inspection** | `inspect` | Core Read-Only API | Read-only inspection of artifacts & capabilities |
| **Inspection** | `lineage` | Module 6 Stage 11 | Historical provenance chain visualization |

## 3. Stepwise Transformation Invariant

```
  CLI Command (e.g. quantum utm aml:<id>)
                 │
                 ▼
        CLIRequestAdapter
                 │ (ApplicationRequest)
                 ▼
    ApplicationContractService
                 │ (Delegates to Core API)
                 ▼
         Core Module (e.g. Module 2)
                 │ (Produces UTM Artifact)
                 ▼
       CLIResponseFormatter (Renders Output & Evidence)
```

The CLI MUST NOT implement transformation algorithms independently. All computational logic resides strictly in the frozen Core (Modules 1–7).
