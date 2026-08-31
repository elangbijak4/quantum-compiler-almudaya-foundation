# Stage 5 Reference State-Vector Execution Engine Specification — Step 1

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Stage:** Stage 5 Implementation — Step 1 Reference State-Vector Engine  
**Status:** STEP 1 COMPLETE  

---

## 1. Primary Objective & Execution Pipeline

Step 1 implements the offline, in-process, ideal reference state-vector execution engine (`ExecutionEngine`). It executes a `NativeCircuitIR` in `STATE_VECTOR` mode to compute exact complex state-vector amplitudes in Hilbert space $\mathcal{H}_N = (\mathbb{C}^2)^{\otimes N}$ ($\text{dim} = 2^N$):

$$\text{NativeCircuitIR} \to \text{ExecutionRequest} \to \text{ExecutionEngine} \to \text{QuantumState} \to \text{ExecutionResult}$$

---

## 2. Bit Indexing Convention

**Big-Endian Basis Indexing Convention:**
- Qubit 0 corresponds to the **Most Significant Bit (MSB)** (bit position $N - 1$).
- Qubit $N - 1$ corresponds to the **Least Significant Bit (LSB)** (bit position 0).
- Bitstring representations (e.g. `'10'`) index qubit 0 as `'1'` and qubit 1 as `'0'`.
- Basis index $i \in [0, 2^N - 1]$ extracts qubit $q$'s bit value via:
  $$\text{bit\_val}(q, i) = \left(i \gg (N - 1 - q)\right) \land 1$$

---

## 3. Mathematical Execution Model & Operation Ordering

- **Hilbert Space:** $\mathcal{H}_N = (\mathbb{C}^2)^{\otimes N}$ with dimension $2^N$.
- **Initial State:** Default $|0\dots0\rangle = (1, 0, \dots, 0)^T$; explicit initial state vectors must satisfy $\text{dim} = 2^N$ and $\|\psi_0\| = 1.0 \pm 10^{-12}$.
- **Strict Canonical Order:** Native operations are executed in exact order of `operation_index` $G_0, G_1, \dots, G_{m-1}$ such that:
  $$|\psi_\text{out}\rangle = U_{m-1} \dots U_1 U_0 |\psi_0\rangle$$
  No gate reordering, commutation, cancellation, or optimization is performed.

---

## 4. Supported Native Vocabulary Semantics

1. **`X(target)`:** Exchanges amplitudes for basis states where target bit differs ($t \leftrightarrow t \oplus 1$). $X^\dagger X = I$.
2. **`CNOT(control, target)`:** Exchanges target bit amplitudes ONLY when control bit $= 1$. Rejects `control == target`. $\text{CNOT}^\dagger \text{CNOT} = I$.
3. **`SWAP(a, b)`:** Permutes basis state amplitudes exchanging qubit $a$ and $b$ bit values. Rejects $a == b$. $\text{SWAP}^\dagger \text{SWAP} = I$.
4. **`TOFFOLI(c1, c2, target)`:** Exchanges target bit amplitudes ONLY when $c_1 = 1$ and $c_2 = 1$. Rejects any control/target collision. $\text{TOFFOLI}^\dagger \text{TOFFOLI} = I$.
5. **Extended Native Gates ($H, Z, S, T, CZ$):** Exact complex state-vector evolution without external framework dependencies.

---

## 5. Invariants & Failure Localization

- **Normalization Invariant:** Verify $\|\psi_\text{out}\| = 1.0 \pm 10^{-12}$. Failures trigger `NUMERICAL_VERIFICATION_FAILURE`.
- **Determinism:** 100% deterministic; zero random number generation in `STATE_VECTOR` mode.
- **Input Immutability:** `NativeCircuitIR` and `ExecutionRequest` remain strictly un-mutated.
- **Failure Localization:** Operations throwing execution-level errors report operation index, gate name, operands, parameters, and localized error messages under `EXECUTION_SEMANTIC_FAILURE`.
- **Unsupported Modes:** Requests for `SHOT_SAMPLING` or `STATE_VECTOR_AND_SHOTS` in Step 1 return `UNSUPPORTED_EXECUTION_MODE` (deferred to Step 2).
