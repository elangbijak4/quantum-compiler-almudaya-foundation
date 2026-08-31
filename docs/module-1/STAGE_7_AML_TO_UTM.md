# Stage 7 Specification — AML-IR to UTM-IR Translator

## 1. Overview

This document specifies the architecture, state encoding, instruction simulation rules, and simulation invariant contract for the **AML-IR to UTM-IR Translator** ($T: \text{AML-IR} \to \text{UTM-IR}$) in **Stage 7** of **Module 1**.

The translator constructs a deterministic Universal Turing Machine transition system ($M_{UTM}$) from a valid `AMLProgram` (AML-IR) using the Stage 6 UTM model.

---

## 2. AML State Encoding $E: \text{AMLState} \to \text{UTMConfiguration}$

To represent the machine state $S = (PC, R, M, F)$ on the 1-tape infinite UTM memory, we establish a deterministic, sparse tape layout:

### 2.1 Tape Layout & Delimiters
- **Cell `0`**: `"^"` (Start marker)
- **Cell `1`**: `"PC"` (Program Counter label marker)
- **Cell `2`**: `str(PC)` (Current integer Program Counter value)
- **Cell `3`**: `"FLAG_ZERO"` (Zero flag marker)
- **Cell `4`**: `"1"` if `flags.zero == True` else `"0"`
- **Cell `5`**: `"FLAG_HALT"` (Halt flag marker)
- **Cell `6`**: `"1"` if `flags.halted == True` else `"0"`
- **Cell `7`**: `"|"` (Section delimiter)
- **Registers Region ($R0..R15$)**:
  - For $i \in \{0 \dots 15\}$:
    - Cell $8 + 2i$: `"R" + str(i)` (Register name marker)
    - Cell $8 + 2i + 1$: `str(registers["R" + str(i)])` (Register integer value)
- **Cell `40`**: `"|"` (Section delimiter)
- **Memory Region ($M$)**:
  - Cell `41`: `"MEM"` (Memory section marker)
  - For each symbol $k$ in memory:
    - Cell $42 + 2k$: `symbol_k`
    - Cell $43 + 2k$: `value_k`
- **Uninitialized cells**: `"_"` (Blank symbol $B$)

---

## 3. Instruction Simulation Strategy

Each AML opcode at PC line $k$ is simulated by a finite sequence of valid UTM transition rules:

$$\delta_1, \delta_2, \dots, \delta_m$$

### 3.1 State Naming Convention
UTM states for instruction at index $k$ follow the pattern:
- `q_instr_{k}_start`: Entry state for instruction $k$.
- `q_instr_{k}_{substate}`: Internal processing states.
- `q_instr_{k+1}_start`: Entry state for next sequential instruction (or `q_instr_{target_pc}_start` for jumps).

### 3.2 Opcode Transition Mapping Summary
1. **`LOAD R_dst, src`**: Transitions fetch `src` value, update register cell for `R_dst`, update `PC` cell, and branch to `q_next`.
2. **`STORE dst_mem, R_src`**: Transitions read `R_src` value, update memory cell for `dst_mem`, update `PC` cell, and branch to `q_next`.
3. **`MOV R_dst, src`**: Transitions copy `src` to `R_dst` register cell, update `PC` cell, and branch to `q_next`.
4. **`ADD R_dst, src`**: Transitions compute sum, update `R_dst` register cell, update `PC` cell, and branch to `q_next`.
5. **`SUB R_dst, src`**: Transitions compute difference, update `R_dst` register cell, update `PC` cell, and branch to `q_next`.
6. **`MUL R_dst, src`**: Transitions compute product, update `R_dst` register cell, update `PC` cell, and branch to `q_next`.
7. **`CMP R1, src`**: Transitions compare values, set `FLAG_ZERO` cell to `"1"` if equal else `"0"`, update `PC` cell, and branch to `q_next`.
8. **`JMP target`**: Transitions update `PC` cell to `target_pc` and branch directly to `q_instr_{target_pc}_start`.
9. **`JZ target`**: Transitions inspect `FLAG_ZERO` cell; if `"1"` branch to `q_instr_{target_pc}_start`, else branch to `q_next`.
10. **`JNZ target`**: Transitions inspect `FLAG_ZERO` cell; if `"0"` branch to `q_instr_{target_pc}_start`, else branch to `q_next`.
11. **`HALT`**: Transitions update `FLAG_HALT` cell to `"1"` and transition to `q_halt`.

---

## 4. Simulation Invariant Commuting Diagram

For any AML state transition $S_t \xrightarrow{\text{AML step}} S_{t+1}$, there exists a finite UTM transition sequence:

$$E(S_t) \xrightarrow{\text{UTM steps} *} E(S_{t+1})$$

```text
         AML Step
    S_t ───────────→ S_{t+1}
     │                 │
   E │                 │ E
     ▼                 ▼
    C_t ───────────→ C_{t+1}
         UTM Steps *
```

---

## 5. Architectural Boundaries

- **Status after Stage 7:** `TRANSLATION_GENERATED`, `UTM_STRUCTURE_VALID`.
- **Stage 7 Exclusions:** Does NOT execute full multi-step UTM simulation (Stage 8), does NOT generate final certificates (Stage 11), does NOT include reversibility or quantum states.
