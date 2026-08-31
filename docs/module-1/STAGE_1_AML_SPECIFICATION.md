# Stage 1 Specification — Algorithmic Machine Language (AML v0.1)

## 1. Overview

This document establishes the formal definition and syntax specification of **AML v0.1** (Algorithmic Machine Language) as required by **Stage 1** of **Module 1** in the `quantum-compiler` project.

AML v0.1 is a minimal, formal, instruction-level intermediate language designed to bridge algorithmic descriptions and low-level computational state machines (UTM).

---

## 2. Register Model & Memory Model

### 2.1 Registers
- **General Purpose Registers:** `R0`, `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R8`, `R9`, `R10`, `R11`, `R12`, `R13`, `R14`, `R15`.
- Total available registers in AML v0.1: **16 registers** (`R0` through `R15`).
- Register names are case-insensitive in textual representation (e.g., `r1` is equivalent to `R1`), but canonical representation is uppercase `R0`..`R15`.

### 2.2 Memory Addresses & Symbols
- Memory locations can be referenced by integer addresses or alphanumeric symbolic names (e.g., `A`, `B`, `OUT`, `VAR_1`).
- Symbolic names must begin with a letter or underscore, followed by alphanumeric characters or underscores: `[a-zA-Z_][a-zA-Z0-9_]*`.

### 2.3 Immediate Values
- Integer literals formatted in base-10 (e.g., `5`, `-10`, `0`).

---

## 3. Instruction Set Architecture (11 Instructions)

AML v0.1 defines exactly 11 valid opcodes divided into four categories:

### 3.1 Data Movement Instructions
1. **`LOAD`**
   - **Signature:** `LOAD <dst_reg>, <src_mem_or_imm>`
   - **Arity:** 2
   - **Operand 1:** Register (`dst`)
   - **Operand 2:** Memory Label/Symbol OR Immediate Integer (`src`)
   - **Description:** Loads the value from memory location or immediate value into the target register.

2. **`STORE`**
   - **Signature:** `STORE <dst_mem>, <src_reg>`
   - **Arity:** 2
   - **Operand 1:** Memory Label/Symbol (`dst`)
   - **Operand 2:** Register (`src`)
   - **Description:** Stores the value contained in the source register into memory.

3. **`MOV`**
   - **Signature:** `MOV <dst_reg>, <src_reg_or_imm>`
   - **Arity:** 2
   - **Operand 1:** Register (`dst`)
   - **Operand 2:** Register OR Immediate Integer (`src`)
   - **Description:** Copies a value from source register or immediate to destination register.

### 3.2 Arithmetic & Logic Instructions
4. **`ADD`**
   - **Signature:** `ADD <dst_reg>, <src_reg_or_imm>`
   - **Arity:** 2
   - **Operand 1:** Register (`dst`)
   - **Operand 2:** Register OR Immediate Integer (`src`)
   - **Description:** Adds operand 2 to destination register value and stores result in destination register.

5. **`SUB`**
   - **Signature:** `SUB <dst_reg>, <src_reg_or_imm>`
   - **Arity:** 2
   - **Operand 1:** Register (`dst`)
   - **Operand 2:** Register OR Immediate Integer (`src`)
   - **Description:** Subtracts operand 2 from destination register value and stores result in destination register.

6. **`MUL`**
   - **Signature:** `MUL <dst_reg>, <src_reg_or_imm>`
   - **Arity:** 2
   - **Operand 1:** Register (`dst`)
   - **Operand 2:** Register OR Immediate Integer (`src`)
   - **Description:** Multiplies destination register by operand 2 and stores result in destination register.

7. **`CMP`**
   - **Signature:** `CMP <reg1>, <reg2_or_imm>`
   - **Arity:** 2
   - **Operand 1:** Register (`reg1`)
   - **Operand 2:** Register OR Immediate Integer (`reg2`)
   - **Description:** Compares operand 1 and operand 2, setting execution status flags.

### 3.3 Control Flow Instructions
8. **`JMP`**
   - **Signature:** `JMP <target_label_or_imm>`
   - **Arity:** 1
   - **Operand 1:** Memory Label / Target Address (`target`)
   - **Description:** Unconditional jump to target program line/label.

9. **`JZ`**
   - **Signature:** `JZ <target_label_or_imm>`
   - **Arity:** 1
   - **Operand 1:** Memory Label / Target Address (`target`)
   - **Description:** Conditional jump to target if Zero flag is set.

10. **`JNZ`**
    - **Signature:** `JNZ <target_label_or_imm>`
    - **Arity:** 1
    - **Operand 1:** Memory Label / Target Address (`target`)
    - **Description:** Conditional jump to target if Zero flag is NOT set.

### 3.4 Control Instructions
11. **`HALT`**
    - **Signature:** `HALT`
    - **Arity:** 0
    - **Operands:** None
    - **Description:** Halts program execution.

---

## 4. Operand Matrix Summary

| Opcode | Arity | Operand 1 Allowed Types | Operand 2 Allowed Types |
| :--- | :---: | :--- | :--- |
| `LOAD` | 2 | `REGISTER` | `LABEL_OR_ADDRESS`, `IMMEDIATE` |
| `STORE` | 2 | `LABEL_OR_ADDRESS` | `REGISTER` |
| `MOV` | 2 | `REGISTER` | `REGISTER`, `IMMEDIATE` |
| `ADD` | 2 | `REGISTER` | `REGISTER`, `IMMEDIATE` |
| `SUB` | 2 | `REGISTER` | `REGISTER`, `IMMEDIATE` |
| `MUL` | 2 | `REGISTER` | `REGISTER`, `IMMEDIATE` |
| `CMP` | 2 | `REGISTER` | `REGISTER`, `IMMEDIATE` |
| `JMP` | 1 | `LABEL_OR_ADDRESS`, `IMMEDIATE` | N/A |
| `JZ` | 1 | `LABEL_OR_ADDRESS`, `IMMEDIATE` | N/A |
| `JNZ` | 1 | `LABEL_OR_ADDRESS`, `IMMEDIATE` | N/A |
| `HALT` | 0 | N/A | N/A |

---

## 5. Validity & Non-Compliance Criteria

An instruction token set is **INVALID** if:
1. Opcode is not in the set of 11 valid opcodes (e.g. `DIV`, `NOP`, `AND`, `CALL`).
2. Arity mismatch (too few or too many operands provided).
3. Operand type mismatch (e.g., passing an immediate as destination for `STORE`, or invalid register name like `R99`).

---

## 6. Stage Boundary Compliance

Per Stage 1 requirements:
- **Included:** Opcode taxonomy, operand constraints, register domain definition, validation specification.
- **Excluded:** Text parsing, operational semantics execution, UTM state mapping, verification engine, certificate generation.
