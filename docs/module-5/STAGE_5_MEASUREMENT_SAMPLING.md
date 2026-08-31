# Stage 5 Measurement & Seeded Shot Sampling Specification — Step 2

**Module:** Module 5 — Quantum Execution & Backend Integration Layer  
**Stage:** Stage 5 Implementation — Step 2 Measurement & Seeded Shot Sampling  
**Status:** STEP 2 COMPLETE  

---

## 1. Primary Objective & Execution Pipeline

Step 2 implements computational-basis readout measurement, analytical probability extraction, and local PRNG seeded shot sampling (`ShotSampler`) on top of the frozen Step 1 state-vector execution engine (`ExecutionEngine`):

$$\text{NativeCircuitIR} \to \text{ExecutionRequest} \to \text{Step 1 State Vector } \psi \to \text{Probabilities } P(x) \to \text{Seeded Sampling} \to \text{MeasurementResult} \to \text{ExecutionResult}$$

---

## 2. Mathematical Measurement & Probability Model

- **State Representation:** Final state vector $|\psi\rangle = \sum_x \alpha_x |x\rangle$ in Hilbert space $\mathcal{H}_N = (\mathbb{C}^2)^{\otimes N}$.
- **Analytical Probability Extraction:**
  $$P(x) = |\alpha_x|^2 \quad \forall x \in [0, 2^N - 1]$$
- **Normalization Invariant:**
  $$\sum_x P(x) = 1.0 \pm 10^{-12}$$
  Failure to meet normalization triggers `NUMERICAL_VERIFICATION_FAILURE`.
- **Seed Independence:** Analytical probabilities $P(x)$ are purely deterministic functions of state amplitudes and are **100% independent** of the random seed: $P_{\text{seed1}}(x) == P_{\text{seed2}}(x)$.

---

## 3. Seeded Shot Sampling & Reproducibility Contract

- **Local PRNG Instance:** Sampling uses `random.Random(seed)` instantiated locally per sampling request. Global Python random state (`random.seed()`, `random.random()`) is **NEVER** mutated.
- **Reproducibility Guarantee:** For identical circuit $C$, initial state $\psi_0$, shot count $N_\text{shots}$, and seed $S$:
  $$\text{Execute}(C, \text{seed}=S, N) \equiv \text{Execute}(C, \text{seed}=S, N)$$
  `shot_sequence` and `counts` are byte-for-byte identical across repeated runs.
- **Invariants:**
  1. $\text{len}(\text{shot\_sequence}) == N_\text{shots}$
  2. $\sum_{x} \text{counts}[x] == N_\text{shots}$
  3. `shot_count` $== N_\text{shots}$

---

## 4. Execution Mode Semantics

1. **`STATE_VECTOR`:**
   Single state vector evolution pass. Returns `final_state_vector` dict. `measurement_result = None`.
2. **`SHOT_SAMPLING`:**
   Single state vector evolution pass $\to$ analytical probabilities $P(x)$ extraction $\to$ seeded shot sampling. Returns `measurement_result` payload. `final_state_vector = None`.
3. **`STATE_VECTOR_AND_SHOTS`:**
   Single state vector evolution pass. Returns **BOTH** `final_state_vector` and `measurement_result` derived from the same state vector. (Single-pass execution invariant: state vector is NOT evolved twice).

---

## 5. Big-Endian Bitstring Readout

- Qubit 0 is the **Most Significant Bit (MSB)**; Qubit $N-1$ is the **Least Significant Bit (LSB)**.
- Bitstrings in `probabilities`, `counts`, and `shot_sequence` use big-endian ordering (e.g. `'10'` means qubit 0 is 1, qubit 1 is 0).

---

## 6. Failure Semantics & Failure Domain Localization

- `shots <= 0`: Triggers `MEASUREMENT_FAILURE`.
- Un-normalized probabilities: Triggers `NUMERICAL_VERIFICATION_FAILURE`.
- External hardware backend requested: Triggers `FORBIDDEN_HARDWARE_REQUEST`.
- Sampling error: Triggers `MEASUREMENT_FAILURE`.
