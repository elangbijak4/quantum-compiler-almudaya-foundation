# Stage 4 Specification — AML Parser & AML-IR (Intermediate Representation)

## 1. Overview

This document specifies the architecture, data structures, and error reporting rules for the **AML Parser** in **Stage 4** of **Module 1**.

The parser transforms raw textual AML source code into a structured, validated intermediate representation known as **AML-IR** (`AMLProgram`).

---

## 2. AML-IR Data Structures

### 2.1 `AMLInstruction`
Represents an individual executable instruction in the IR:
- **`line_number: int`**: 1-indexed source line number.
- **`pc: int`**: 0-indexed Program Counter position.
- **`label: Optional[str]`**: Symbolic label associated with this instruction (if any).
- **`opcode: Opcode`**: Standardized Opcode enum.
- **`operands: List[str]`**: Validated list of operand string tokens.

### 2.2 `AMLProgram` (AML-IR)
Represents the complete parsed AML program:
- **`instructions: List[AMLInstruction]`**: Ordered list of parsed instructions.
- **`label_table: Dict[str, int]`**: Mapping from label symbols to target instruction PC index.
- **`symbol_table: Set[str]`**: Set of referenced memory symbols/labels.
- **`source_hash: str`**: Deterministic SHA-256 hash of normalized source text (used for certificate provenance).

---

## 3. Parser Pipeline Architecture (3-Pass Parser)

```text
Raw Source Text
      ↓
Pass 1: Line-by-Line Lexical Analysis & Tokenization (tokenize_line)
      ↓
Pass 2: EBNF Line Grammar Validation & Label Registration (validate_line_grammar)
      ↓
Pass 3: Opcode Specification Validation & AML-IR Assembly (validate_instruction_spec)
      ↓
AMLProgram (AML-IR)
```

---

## 4. Error Handling Conventions

The parser raises `ParseError` containing:
- **`line_number: int`**: Line number where the error occurred.
- **`message: str`**: Explicit, descriptive error message.

Errors must NEVER be swallowed silently.

---

## 5. Stage Boundary Verification

- **Included:** Source text parsing, syntax validation, label resolution table, deterministic SHA-256 source hashing, `AML-IR` assembly.
- **Excluded:** AML Interpreter execution loop (Stage 5), UTM-IR translation (Stage 7).
