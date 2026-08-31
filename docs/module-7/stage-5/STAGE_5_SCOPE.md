# MODULE 7 STAGE 5 — SCOPE BOUNDARY

## In Scope
- Result validation and normalization verification.
- Normalized empirical probability distribution construction ($P(x) = \text{count}(x) / N$).
- Hellinger distance and KS distance calculations comparing $P_{\text{observed}}$ vs $P_{\text{reference}}$.
- Threshold evaluation under versioned `StatisticalVerificationPolicy`.
- Generation of immutable `StatisticalVerificationRecord`.
- Appending verification events to Module 6 Stage 11 repository.

## Out of Scope (Forbidden)
- Circuit lowering, gate decomposition, or routing (Stage 2 authority).
- Local virtual reference simulation (Stage 3 authority).
- Cloud hardware submission or adapter management (Stage 4 authority).
- Automatic re-execution, automatic shot tuning, or automatic threshold relaxation.
- Automatic backend substitution or error mitigation post-selection.
