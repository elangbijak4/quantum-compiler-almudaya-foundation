# Stage 8 Specification — UTM $\to$ RUTM Equivalence Verification Gate

**Module:** Module 2 (UTM $\to$ Reversible UTM)  
**Stage:** Stage 8 — UTM $\to$ RUTM Equivalence Verification Gate (Micro Closure Patch)  
**Status:** COMPLETE / FROZEN READY  
**Governing Documents:** [`main-technical-refference.md`](../../main-technical-refference.md), [`STAGE_4_RUTM_REVERSIBILITY_PROOF.md`](STAGE_4_RUTM_REVERSIBILITY_PROOF.md), [`STAGE_5_RUTM_IR.md`](STAGE_5_RUTM_IR.md), [`STAGE_6_UTM_TO_RUTM_TRANSLATION.md`](STAGE_6_UTM_TO_RUTM_TRANSLATION.md), [`STAGE_7_RUTM_EXECUTION.md`](STAGE_7_RUTM_EXECUTION.md)  
**Implementation Package:** [`src/module2/verification/`](../../src/module2/verification/)  

---

## 1. Purpose

Stage 8 constructs the complete end-to-end **UTM $\to$ RUTM Equivalence Verification Gate**. The gate determines whether a translated Reversible UTM (`RUTM_IR`) preserves the observable computational behavior of its source classical Universal Turing Machine (`UTMProgram`) over a defined finite execution domain.

$$\text{UTM-IR} \xrightarrow{\quad T_{UR} \quad} \text{RUTM-IR} \xrightarrow{\quad \text{execute\_rutm\_ir()} \quad} \text{RUTM Trace } [C_{R,i}] \xrightarrow{\quad \pi_{\text{UTM}} \quad} \text{Projected } C_{U,i} \stackrel{?}{==} \text{Source } C_{U,i}$$

---

## 2. Critical Architectural Distinction

> [!IMPORTANT]
> **VERIFICATION GATE ONLY:**  
> Stage 8 is a verification gate and does **NOT** invent new execution semantics, translation algorithms, or reversibility proofs.  
> It reuses Module 1 UTM semantics (`step_utm_configuration`), Stage 4 projection ($\pi_{\text{UTM}}$), Stage 6 translation (`translate_utm_to_rutm`), and Stage 7 execution (`execute_rutm_ir`).

---

## 3. Verification Pipeline & Three-Valued Outcome

The gate function `verify_utm_to_rutm_equivalence(utm_program, initial_utm_config, max_steps)` executes the complete pipeline:

```
[Validate Source UTM] -> [Translate T_UR] -> [Validate RUTM-IR] -> [Map Initial Config]
          |
          +-> [Execute Source UTM]  ---\
          +-> [Execute Target RUTM] ---> [Project pi_UTM] -> [Compare Traces] -> [Classify Status]
```

### Outcome Classification & Precedence Rules (Patch B):
1. **Actual Step Semantic Mismatch / Runtime Error:**  
   If $\pi_{\text{UTM}}(C_{R,i}) \neq C_{U,i}$ or defined runtime error occurs $\to$ `status="FAIL"`, `equivalent=False`, `mismatch_step` set.
2. **Terminal Halt Mismatch:**  
   If $\text{source\_halted} \neq \text{target\_halted}$ (e.g. source non-halting, target halted or vice versa) $\to$ `status="FAIL"`, `equivalent=False`. **(Has precedence over resource limit INCONCLUSIVE)**.
3. **Normal Execution Equivalence:**  
   If both executions halt normally, all compared steps match, and trace lengths agree $\to$ `status="PASS"`, `equivalent=True`.
4. **Resource Exhaustion without Mismatch:**  
   If neither execution halted up to `max_steps` and no mismatch occurred $\to$ `status="INCONCLUSIVE"`, `resource_limit_reached=True`.

---

## 4. Distinction Between Failure Categories (Patch A)

- **Runtime Error (`test_10` & `test_16`):** Occurs when a machine encounters an undefined transition or invalid configuration $\to$ `status="FAIL"`.
- **Projection Step Semantic Mismatch (`test_21`):** Occurs when target projected state/tape/head differs from source UTM at step $i \to$ `status="FAIL"`, `mismatch_step=i`.
- **Terminal Halt Mismatch (`test_22`):** Occurs when source and target halting statuses diverge at termination $\to$ `status="FAIL"`.

---

## 5. Reversibility & Proof Boundaries

1. **Formal Proof Boundary:** Universal mathematical claims ($R_P^{-1} \circ R_P = \text{id}$) are established in Stage 4. Stage 8 provides executable finite-domain verification.
2. **Certificate Boundary:** Stage 8 returns `EquivalenceVerificationResult` with provenance metadata; formal certificate generation is deferred to future stages.

---

## 6. Determinism & Negative Rejection

- **Determinism:** Repeated execution of the gate on identical inputs produces identical `EquivalenceVerificationResult` status, step counts, and diagnostic error strings.
- **Negative Rejection:** Deliberate semantic mismatches in source vs target configurations or execution steps are immediately caught, producing `status="FAIL"` with non-null `mismatch_step`.

---

## 7. Stage 9 Prerequisites

Before proceeding to **Stage 9 (Module 2 Completion Gate)**:
1. All 22 tests in `tests/module2/test_stage8_equivalence.py` must PASS.
2. All 140 Module 2 tests must PASS.
3. All 79 frozen Module 1 regression tests must PASS.
4. Obtain explicit user authorization to advance to Stage 9.
