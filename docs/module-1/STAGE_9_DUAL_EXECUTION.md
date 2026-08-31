# Stage 9 Specification — Dual Execution Orchestration

## 1. Overview

This document specifies the architecture and data structures for **Dual Execution Orchestration** in **Stage 9** of **Module 1**.

Stage 9 provides the orchestration layer that executes a single AML source program through both compiler execution pathways simultaneously:

```text
                        AML Source Code
                               │
                       parse_aml_source()
                               │
                           AMLProgram
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
      AML Interpreter                   AML -> UTM Translator
   (Reference Semantics)                (Stage 7 Transformation)
            │                                     │
    AMLInterpreterResult                      UTMProgram
            │                                     │
            │                               UTM Simulator
            │                           (Stage 8 Execution)
            │                                     │
            │                             UTMExecutionResult
            └──────────────────┬──────────────────┘
                               ▼
                      DualExecutionResult
```

---

## 2. Dual Execution Data Structures

### 2.1 `DualExecutionResult`
Represents the packaged side-by-side results from both execution pathways:
- **`aml_result: Optional[AMLInterpreterResult]`**: Result of reference execution via `AMLInterpreter`.
- **`translation_result: Optional[TranslationResult]`**: Result of `AML-IR -> UTM-IR` translation.
- **`utm_result: Optional[UTMExecutionResult]`**: Result of target simulation via `UTMSimulator`.
- **`source_hash: str`**: SHA-256 hash of the input AML source text.
- **`status: str`**: Pipeline execution status (`"DUAL_EXECUTION_COMPLETED"`, `"PARSER_ERROR"`, `"TRANSLATION_ERROR"`, `"SIMULATOR_ERROR"`).
- **`error: Optional[str]`**: Error description if any stage failed.

---

## 3. Orchestration Algorithm (`execute_dual_pipeline`)

1. Parse source code using `parse_aml_source(source_text)` $\implies$ `AMLProgram`.
2. Execute reference pathway using `AMLInterpreter().execute(program, initial_memory, aml_max_steps)` $\implies$ `AMLInterpreterResult`.
3. Execute translation pathway using `translate_aml_to_utm(program)` $\implies$ `TranslationResult`.
4. Encode initial UTM configuration using `encode_aml_state(aml_result.final_state_initial)` $\implies$ `UTMConfiguration`.
5. Execute target pathway using `simulate_utm(translation_result.utm_program, initial_utm_config, utm_max_steps)` $\implies$ `UTMExecutionResult`.
6. Package and return `DualExecutionResult`.

---

## 4. Stage Boundary Verification

- **Included:** Side-by-side execution orchestration, result aggregation into `DualExecutionResult`.
- **Excluded:** Automatic semantic equivalence evaluation (Stage 10), certificate generation (Stage 11).
