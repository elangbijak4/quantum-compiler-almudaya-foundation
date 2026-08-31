# Module 6 Stage 6 — Governed Vocabulary Promotion Policy

## 1. Executive Summary

Governed Promotion establishes a strict, auditable boundary controlling how candidate gates analyzed in Stage 5 transition into the production evolutionary vocabulary $GE(k)$.

---

## 2. Governed Flow vs Forbidden Automatic Mutation

### 2.1 Authorized Flow
$$\text{Candidate} \to \text{Validation} \to \text{Expressibility Analysis} \to \text{Equivalence Analysis} \to \text{Evidence Classification} \to \text{Recommendation} \to \text{Explicit Authorization} \to \text{PromotionRecord} \to GE(k+1)$$

### 2.2 Forbidden Automatic Mutation
$$\text{Candidate} \to \text{Automatic Registration} \to \text{Production Mutation} \quad \mathbf{[FORBIDDEN]}$$

---

## 3. Promotion Record Requirements

Every promotion event requires an immutable `PromotionRecord` with:
- `promotion_id`
- `parent_evolution_stage`
- `candidate_gate_ids` & `candidate_hashes`
- `evidence_reference` & `equivalence_reference`
- `authorization_status`: MUST be `EXPLICITLY_AUTHORIZED`
- `authorized_by` & `promotion_timestamp`
- `resulting_vocabulary_hash`

---

## 4. Implementation Files

- [`src/module6/evolution/promotion.py`](file:///d:/quantum-compiler/src/module6/evolution/promotion.py): `PromotionRecord` & `PromotionAuthorizationStatus`.
- [`src/module6/evolution/lineage.py`](file:///d:/quantum-compiler/src/module6/evolution/lineage.py): `EvolutionaryLineageManager.promote_candidates()`.

---

## 5. Verification Evidence

- [`tests/module6/test_stage6_promotion.py`](file:///d:/quantum-compiler/tests/module6/test_stage6_promotion.py): Verified governed promotion boundary.
- **Status**: `PASS`
