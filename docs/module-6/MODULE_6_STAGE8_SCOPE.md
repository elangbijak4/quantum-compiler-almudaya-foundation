# MODULE 6 STAGE 8 — SCOPE AND BOUNDARIES

## 1. Scope (Included)

1. **Circuit Cost Evaluation**:
   - `CircuitCostEvaluator` calculating gate counts, depth, T-depth, CNOT-depth, and qubit width.
2. **Canonical Algebraic Rewriting**:
   - Self-inverse gate cancellation (X-X, CNOT-CNOT, H-H).
   - Identity gate elimination.
   - Adjacent phase fusion.
3. **Vocabulary Containment Verification**:
   - Verifying all gates in $Q_{\text{opt}}$ belong to $G_{\text{effective}}$.
4. **Stage 4 Level 6 Semantic Equivalence Verification**:
   - Verifying $Q_{\text{opt}} \equiv_Q Q_{\text{orig}}$.
5. **Canonical Serialization & Deterministic Provenance**:
   - SHA-256 report hashing, JSON round-trip serialization (`deserialize(serialize(X)) == X`).
6. **Governance & Test Infrastructure**:
   - 10 governance documents and unit test suite in `tests/module6/test_stage8_*.py`.

---

## 2. Non-Scope (Explicitly Excluded)

1. **No Production Implementation During Initialization**: Production engine code remains stubbed / unexecuted until formal scope review.
2. **No Upstream Code Mutations**: Zero edits to `src/module1/` .. `src/module5/`.
3. **No Automatic Vocabulary Promotion**: Optimization does NOT trigger gate promotion in $GE(k)$.
4. **No Physical QPU Execution**: Zero hardware deployment.
5. **No Noise Simulation**: Pure logical analytical model.
