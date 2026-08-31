# Stage 3 Specification — AML v0.1 Operational Semantics

## 1. Machine State Model

The operational state of the AML machine is formally represented as a tuple:

$$S = (PC, R, M, F)$$

where:
- **$PC \in \mathbb{N}_0$**: Program Counter indicating the 0-indexed instruction position.
- **$R: \text{Register} \to \mathbb{Z}$**: Mapping from register names (`R0`..`R15`) to integer values. Initially $R[r] = 0$ for all $r$.
- **$M: \text{Symbol} \to \mathbb{Z}$**: Memory mapping from symbolic labels/addresses to integer values.
- **$F = (zero: \text{Bool}, halted: \text{Bool}, error: \text{Optional}[\text{String}])$**: Status flags and execution control state. Initially $(False, False, None)$.

---

## 2. Operational Semantics Transition Rules $\langle I, S \rangle \to S'$

For an instruction $I$ at current state $S = (PC, R, M, F)$, the state transition function computes $S' = (PC', R', M', F')$.

### 2.1 Data Movement Instructions

#### 1. `LOAD R_dst, src`
- If $src$ is a register: $val = R[src]$
- Else if $src$ is an immediate: $val = src$
- Else if $src$ is a memory label: $val = M[src]$
- **State Update:**
  - $R'[R_{dst}] = val$
  - $PC' = PC + 1$

#### 2. `STORE dst_mem, R_src`
- **State Update:**
  - $M'[dst\_mem] = R[R_{src}]$
  - $PC' = PC + 1$

#### 3. `MOV R_dst, src`
- If $src$ is a register: $val = R[src]$
- Else if $src$ is an immediate: $val = src$
- **State Update:**
  - $R'[R_{dst}] = val$
  - $PC' = PC + 1$

---

### 2.2 Arithmetic & Logic Instructions

#### 4. `ADD R_dst, src`
- $val = R[src]$ if $src \in \text{Register}$ else $src$
- **State Update:**
  - $R'[R_{dst}] = R[R_{dst}] + val$
  - $PC' = PC + 1$

#### 5. `SUB R_dst, src`
- $val = R[src]$ if $src \in \text{Register}$ else $src$
- **State Update:**
  - $R'[R_{dst}] = R[R_{dst}] - val$
  - $PC' = PC + 1$

#### 6. `MUL R_dst, src`
- $val = R[src]$ if $src \in \text{Register}$ else $src$
- **State Update:**
  - $R'[R_{dst}] = R[R_{dst}] \times val$
  - $PC' = PC + 1$

#### 7. `CMP R1, src`
- $val = R[src]$ if $src \in \text{Register}$ else $src$
- **State Update:**
  - $F'.zero = (R[R_1] == val)$
  - $PC' = PC + 1$

---

### 2.3 Control Flow Instructions

#### 8. `JMP target`
- $target\_pc = target$ (if target is integer PC line) or resolved label location.
- **State Update:**
  - $PC' = target\_pc$

#### 9. `JZ target`
- **State Update:**
  - If $F.zero == True$: $PC' = target\_pc$
  - Else: $PC' = PC + 1$

#### 10. `JNZ target`
- **State Update:**
  - If $F.zero == False$: $PC' = target\_pc$
  - Else: $PC' = PC + 1$

---

### 2.4 Control Instructions

#### 11. `HALT`
- **State Update:**
  - $F'.halted = True$
  - $PC' = PC$

---

## 3. Stage Boundary Compliance

- **Included:** Operational machine state model $S = (PC, R, M, F)$ and small-step operational transition function.
- **Excluded:** Multi-line AST parser, program loader, UTM machine mapping.
