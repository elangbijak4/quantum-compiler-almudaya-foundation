# Stage 2 Specification — AML v0.1 Textual Grammar & Lexical Specification

## 1. Overview

This document specifies the formal EBNF (Extended Backus-Naur Form) grammar, lexical rules, and line-level tokenization principles for **AML v0.1** (Algorithmic Machine Language) as required by **Stage 2** of **Module 1**.

---

## 2. Formal EBNF Grammar Specification

```ebnf
(* AML Program Syntax *)
Program          ::= ( Statement | EmptyLine )* ;

EmptyLine        ::= [ WhiteSpace ] [ Comment ] NewLine ;
Statement        ::= [ WhiteSpace ] [ LabelDecl ] [ WhiteSpace ] [ Instruction ] [ WhiteSpace ] [ Comment ] NewLine ;

LabelDecl        ::= Identifier ":" ;

Instruction      ::= Opcode [ WhiteSpace OperandList ] ;
OperandList      ::= Operand ( [ WhiteSpace ] "," [ WhiteSpace ] Operand )* ;

Operand          ::= Register | Immediate | Identifier ;

(* Lexical Tokens *)
Opcode           ::= "LOAD" | "STORE" | "MOV" | "ADD" | "SUB" | "MUL" | "CMP" | "JMP" | "JZ" | "JNZ" | "HALT" ;
Register         ::= ("R" | "r") ( "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "11" | "12" | "13" | "14" | "15" ) ;
Immediate        ::= [ "-" ] Integer ;
Identifier       ::= ( Letter | "_" ) ( Letter | Digit | "_" )* ;

Comment          ::= "#" { AnyCharacterExceptNewLine } ;

Integer          ::= Digit+ ;
Digit            ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
Letter           ::= "a".."z" | "A".."Z" ;
WhiteSpace       ::= ( " " | "\t" )+ ;
NewLine          ::= "\n" | "\r\n" ;
```

---

## 3. Lexical Token Categories

A line of AML text is tokenized into a sequence of discrete lexical tokens:

1. **`TOKEN_LABEL_DECL`**: A label identifier followed immediately by a colon `:` (e.g., `START:`, `LOOP_1:`).
2. **`TOKEN_OPCODE`**: One of the 11 recognized opcode strings in uppercase/case-insensitive form (e.g., `LOAD`, `ADD`, `HALT`).
3. **`TOKEN_REGISTER`**: Valid register name (`R0`..`R15`).
4. **`TOKEN_IMMEDIATE`**: Signed integer literal (e.g., `42`, `-10`, `0`).
5. **`TOKEN_SYMBOL`**: Alphanumeric identifier used as memory label or address target (e.g., `A`, `VAR_X`).
6. **`TOKEN_COMMA`**: The comma delimiter `,` separating operands.
7. **`TOKEN_COMMENT`**: Text starting with `#` continuing to the end of line.

---

## 4. Deterministic Parsing Rules for Line Grammar

### Rule 2.1: Comment Stripping
Comments start with `#` and extend to line end. They are ignored for semantic interpretation but recorded as lexical comment tokens.

### Rule 2.2: Label Declarations
A label declaration must appear at the beginning of an instruction or on its own line (e.g. `START:`). A label cannot be placed after an opcode.

### Rule 2.3: Operand Separation
Multiple operands MUST be separated by a comma `,`. Missing commas between operands (e.g. `LOAD R1 A`) is a syntax error.

### Rule 2.4: Indentation and Case Sensitivity
- Leading and trailing whitespace (spaces, tabs) is non-semantic and ignored.
- Opcodes and registers are case-insensitive (e.g. `load r1, a` is canonicalized to `LOAD R1, A`).
- Symbolic labels are case-sensitive (e.g. `VarA` is distinct from `vara`).

---

## 5. Stage Boundary Verification

- **Stage 2 Scope:** Grammar definition, lexical token types, line-level syntax validation rules.
- **Stage 3 Scope (Next):** Operational semantics state transitions.
- **Stage 4 Scope (Later):** Complete AST parser construction.
