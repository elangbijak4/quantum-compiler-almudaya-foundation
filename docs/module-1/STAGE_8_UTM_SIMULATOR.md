# Stage 8 Specification — Universal Turing Machine Simulator

## 1. Overview

This document specifies the architecture, execution loop, halting semantics, and resource metrics for the **Universal Turing Machine Simulator** in **Stage 8** of **Module 1**.

The UTM Simulator provides an executable realization of the Stage 6 UTM model ($M_{UTM} = (Q, \Sigma, \Gamma, \delta, q_0, B, q_{halt})$) and executes `UTMProgram` instances translated from AML in Stage 7.

---

## 2. Simulator Data Structures

### 2.1 `UTMExecutionResult`
Represents the complete result of executing a UTM program:
- **`final_configuration: UTMConfiguration`**: Final machine configuration state $C_t = (q, \text{tape}, h)$.
- **`status: str`**: Execution status string:
  - `"SUCCESS"`: Program reached halt state $q_{halt}$.
  - `"RESOURCE_LIMIT"`: Execution exceeded `max_steps` limit before halting.
  - `"INVALID_TRANSITION"`: Active state and symbol lack a defined transition in $\delta$.
  - `"ERROR"`: Program structural error or configuration error.
- **`halted: bool`**: True if $q == q_{halt}$.
- **`step_count: int`**: Actual count of individual UTM transition steps executed.
- **`tape_usage: int`**: Number of non-blank tape cells occupied or touched in final configuration.
- **`execution_trace: Optional[List[Dict[str, Any]]]`**: Optional step-by-step trace entries.
- **`error: Optional[str]`**: Error details string if applicable.

---

## 3. Simulator Execution Loop

```text
Given UTMProgram M and initial configuration C0:
Initialize step_count = 0, C = C0.copy()
Optional trace_log = []

While step_count < max_steps:
  If C.halted == True: Return SUCCESS
  If C.error != None: Return INVALID_TRANSITION or ERROR
  
  Read symbol a = C.get_tape_symbol()
  Lookup (C.current_state, a) in M.transitions:
    If not found and C.current_state != M.halt_state:
      Set C.error = "Undefined transition"
      Return INVALID_TRANSITION
      
  If enable_trace:
    Record trace entry (step, state_before, symbol_read, action, head_after, state_after)

  C = step_utm_configuration(C, M)
  
If loop completes without HALT:
  Return RESOURCE_LIMIT
```

---

## 4. Resource & Tape Metrics Definitions

### 4.1 Step Count Metric
Counts actual UTM single-step transitions $C_0 \xrightarrow{\delta} C_1 \xrightarrow{\delta} \dots \xrightarrow{\delta} C_t$.
$$\text{step\_count} = t$$

### 4.2 Tape Usage Metric
Defined as the total number of tape indices $i \in \mathbb{Z}$ whose value is not equal to the blank symbol $B$:
$$\text{tape\_usage} = |\{i \in \text{tape.keys()} \mid \text{tape}[i] \neq B\}|$$

---

## 5. Architectural & Stage Boundaries

- **Status after Stage 8:** `UTM_EXECUTED`, `STAGE_8_COMPLETE`.
- **Stage 8 Exclusions:** Does NOT perform Dual Execution comparison with AML Interpreter (Stage 9), does NOT verify semantic equivalence $\text{Sem}_{\text{AML}} = \text{Sem}_{\text{UTM}}$ (Stage 10), does NOT generate certificates (Stage 11), does NOT include reversibility or quantum computational models.
