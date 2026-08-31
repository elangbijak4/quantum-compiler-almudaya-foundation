# Module 6 Stage 6 — User Session Baseline & Lifecycle

## 1. Executive Summary

Stage 6 introduces temporary user session baselines $B_u \subseteq GE(k)$ that allow users to configure or restrict the gate vocabulary permitted during a compilation session without mutating the underlying evolutionary state $GE(k)$.

---

## 2. Core Principles

1. **Session Baseline Constraint**: A user-selected baseline $B_u$ is a **constraint on compilation**, NOT a guarantee of compilation feasibility.
2. **Evolution Immutability**: No session operation (`create_session`, `select_user_baseline`, `reset_baseline`, `end_session`) may mutate $GE(k)$.
   $$\text{hash}(GE_{\text{before}}) == \text{hash}(GE_{\text{after}})$$
3. **Effective Vocabulary Resolution**:
   - `DEFAULT_EVOLUTIONARY`: $G_{\text{effective}} = GE(k)$
   - `USER_SELECTED`: $G_{\text{effective}} = B_u \subseteq GE(k)$

---

## 3. Implementation Files

- [`src/module6/session/baseline.py`](file:///d:/quantum-compiler/src/module6/session/baseline.py): `SessionBaseline` & `BaselineMode`.
- [`src/module6/session/resolver.py`](file:///d:/quantum-compiler/src/module6/session/resolver.py): `EffectiveVocabularyResolver`.
- [`src/module6/session/lifecycle.py`](file:///d:/quantum-compiler/src/module6/session/lifecycle.py): `SessionLifecycle` manager.
- [`src/module6/session/serialization.py`](file:///d:/quantum-compiler/src/module6/session/serialization.py): Canonical JSON serialization.

---

## 4. Verification Evidence

- [`tests/module6/test_stage6_session.py`](file:///d:/quantum-compiler/tests/module6/test_stage6_session.py): Verified session lifecycle and baseline immutability.
- [`tests/module6/test_stage6_resolver.py`](file:///d:/quantum-compiler/tests/module6/test_stage6_resolver.py): Verified effective vocabulary resolution.
- **Status**: `PASS`
