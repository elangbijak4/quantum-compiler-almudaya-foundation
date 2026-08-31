# Module 6 Stage 5 — Expressive Extension Evidence Report

## 1. Executive Summary

This document presents empirical and theoretical evidence gathered by the Module 6 Stage 5 analytical framework evaluating candidate primitive gate extensions for the classical-to-quantum compiler.

---

## 2. Tested Candidate Gate Extensions

| Candidate ID | Gate Name | Matrix Representation | Superposition | Complex Phase | Classification | Evidence Class |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `cand_h` | `HADAMARD` | $\frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$ | Yes | No | `EMPIRICAL_EXTENSION` | `EMPIRICAL_EXPERIMENT` |
| `cand_s` | `PHASE_S` | $\begin{pmatrix}1&0\\0&i\end{pmatrix}$ | No | Yes | `EMPIRICAL_EXTENSION` | `EMPIRICAL_EXPERIMENT` |
| `cand_t` | `T_GATE` | $\begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix}$ | No | Yes | `EMPIRICAL_EXTENSION` | `EMPIRICAL_EXPERIMENT` |
| `cand_x` | `X` | $\begin{pmatrix}0&1\\1&0\end{pmatrix}$ | No | No | `REDUNDANT` | `EMPIRICAL_EXPERIMENT` |
| `cand_cnot` | `CNOT` | Standard 4x4 CNOT | No | No | `REDUNDANT` | `EMPIRICAL_EXPERIMENT` |

---

## 3. Detailed Hadamard Analysis

- **Hadamard Matrix**: $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$
- **Action on Computational Basis**:
  - $H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$ (Norm = $1.000000000000$)
  - $H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$ (Norm = $1.000000000000$)
- **Unitarity Residual**: $\|H^\dagger H - I\|_F = 0.000000000000 < 10^{-12}$
- **Expressive Gain**:
  - Baseline Image Cardinality $|Img_N(F_{G0})| = 8$ (Permutations only)
  - Extended Image Cardinality $|Img_{N}(F_{G_H})| = 24$
  - Expressive Gain Delta $\Delta Img = +16$
  - Target Coverage ($H, S, T$): Baseline = $0\%$, Extended = $33.3\%$ (Hadamard target reached)
- **Backward Compatibility**: $Img_N(F_{G0}) \subseteq Img_N(F_{G_H})$ **VERIFIED PASS**

---

## 4. Complex Amplitude Extension Analysis

- **Phase Gate $S$**:
  - $S|1\rangle = i|1\rangle$
  - Breaks baseline real-amplitude invariant ($U_{F(A)} \in M_{2^N}(\mathbb{R})$).
  - Classification: `EMPIRICAL_EXTENSION`
- **$T$ Gate**:
  - $T|1\rangle = e^{i\pi/4}|1\rangle$
  - Introduces non-Clifford phase shift and complex amplitudes.
  - Classification: `EMPIRICAL_EXTENSION`

---

## 5. Summary of Policy Invariants & Safeguards

1. **Base Vocabulary Immutability**: $G_0$ hash before and after execution: `5a8f9c...` == `5a8f9c...` (VERIFIED).
2. **Safeguard Enforcement**: All finite candidate extensions are classified strictly as `EMPIRICAL_EXTENSION` due to absence of non-sample formal proofs.
3. **No Automatic Promotion**: Zero candidate gates were registered as production primitives; Module 1–5 source code remains untouched.
