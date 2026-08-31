# Stage 5 Specification — AML Reference Interpreter

## 1. Overview

This document specifies the architecture, execution loop, and resource control of the **AML Reference Interpreter** in **Stage 5** of **Module 1**.

The AML Interpreter acts as the **executable reference semantics** ($\text{Sem}_{\text{AML}}$) for Module 1. Its output represents the ground-truth observable result against which the translated UTM simulation will be verified in Stage 10.

---

## 2. Interpreter Data Structures

### 2.1 `AMLInterpreterResult`
Represents the complete result of executing an AML program:
- **`final_state: AMLState`**: End machine state $S = (PC, R, M, F)$.
- **`observable_output: Dict[str, int]`**: Final memory state dictionary.
- **`step_count: int`**: Total number of AML operational instruction steps executed.
- **`status: str`**: Execution status string:
  - `"SUCCESS"`: Program halted normally.
  - `"RESOURCE_LIMIT"`: Step limit `max_steps` exceeded.
  - `"ERROR"`: Operational execution error occurred.

---

## 3. Interpreter Execution Algorithm

```text
Initialize Machine State S0 = (PC=0, R=0, M=initial_memory, F=Default)
Loop step from 0 to max_steps:
  If S.flags.halted == True: Return SUCCESS
  If S.flags.error != None: Return ERROR
  Fetch instruction at PC: I = program.instructions[PC]
  Compute step transition: S' = step_operational_semantics(S, I.opcode, I.operands, program.label_table)
If loop completes without HALT: Return RESOURCE_LIMIT
```

---

## 4. Stage Boundary Verification

- **Included:** Sequential instruction execution loop, initial memory injection, `max_steps` enforcement, observable output extraction.
- **Excluded:** UTM-IR translation (Stage 7), UTM simulation (Stage 8), semantic equivalence verifier (Stage 10).
